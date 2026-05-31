from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_community.utilities import SerpAPIWrapper
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.tools import tool, Tool  # FIXED: Added Tool here, removed old import
from dotenv import load_dotenv
import base64
import sqlite3
import requests
import os
import json
import time 
import sys

load_dotenv() 
os.environ['LANGCHAIN_PROJECT'] = 'chatbot-project'

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY not set in environment")


# Initialize SerpAPI wrapper
serpapi_instance = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)

# -------------------
# 2. Initialize LLM
# -------------------
model = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.5,
    max_tokens=1000
)


from langchain_community.tools import DuckDuckGoSearchRun

# Initialize the tool directly. LangChain will handle the argument mapping.
ddg_tool = DuckDuckGoSearchRun(description="A privacy-respecting search engine. Use this for general web searches.")


# SerpAPI tool with logging
def serpapi_with_logging(query: str) -> str:
    print(f"[LOG] Running SerpAPI Search with query: {query}")
    return serpapi_instance.run(query)


serpapi_tool = Tool(
    name="SerpAPI_Search",
    func=serpapi_with_logging,
    description="A real-time search engine. Use this to get up-to-date factual web search results."
)


# Tavily tool with logging
tavily_tool = TavilySearch(
    max_results=5,
    include_images=True,
    log_searches=True,
    description="An AI-optimized search engine. Best for complex, multi-step research questions."
)


SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


@tool
def search_youtube_videos(query: str) -> str:
    """
    Searches YouTube for videos based on a user's query.
    Use this tool whenever a user asks for videos and tutorials on a specific topic.
    Returns a JSON string containing a list of video details, including titles,
    links, and thumbnail URLs.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return json.dumps({"error": "YouTube API key not found."})

    try:
        # Build the YouTube service object
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Perform the search
        search_request = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=5  # Fetch up to 5 videos
        )
        search_response = search_request.execute()

        videos = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            thumbnails = item["snippet"]["thumbnails"]
            
            # Get the best available thumbnail URL
            thumbnail_url = thumbnails.get("high", {}).get("url") or thumbnails.get("default", {}).get("url", "")
            
            videos.append({
                "title": title,
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumbnail_url
            })
            
        # Return the results as a JSON string, as this is a robust format for tool outputs
        return json.dumps(videos)

    except HttpError as e:
        return json.dumps({"error": f"An API error occurred: {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

#---------------------------------
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
if not HUGGINGFACE_TOKEN:
    raise ValueError("HUGGINGFACE_TOKEN not set in environment. This is required for image generation.")

@tool
def generate_stability_image(prompt: str, negative_prompt: str = "blurry, low quality, text, watermark") -> str:
    """
    Generates a high-quality, realistic image from a text prompt using Stable Diffusion XL.
    Use this tool whenever a user asks to create, draw, or generate an image.
    The prompt should be descriptive for best results.
    Returns a JSON string containing the Base64 encoded image data.
    """
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {"negative_prompt": negative_prompt}
    }
    
    print(f"Generating image with prompt: '{prompt}'")
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        
        if response.status_code == 200:
            image_bytes = response.content
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            print("Image generated successfully.")
            return json.dumps({"image_data": image_base64, "format": "jpeg"})
        else:
            error_message = response.json().get("error", response.text)
            print(f"Image generation failed: {error_message}")
            return json.dumps({"error": f"Failed to generate image: {error_message}"})
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"API connection error: {e}")
        coming_soon_msg = """🎨 Image Generation - Coming Soon

Image generation service is temporarily unavailable.
We're working on bringing this feature back online."""
        return json.dumps({"coming_soon": True, "message": coming_soon_msg, "feature": "image_generation"})
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        coming_soon_msg = """🎨 Image Generation - Coming Soon

Image generation service is temporarily unavailable.
We're working on bringing this feature back online."""
        return json.dumps({"coming_soon": True, "message": coming_soon_msg, "feature": "image_generation"})


# Calculator tool
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """Perform basic arithmetic operations: add, sub, mul, div"""
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# -------------------
# 5. Deep Agent Integration
# -------------------
DEEP_AGENT_URL = os.getenv("DEEP_AGENT_URL", "https://deep-agent-service.onrender.com/deep-task")
DEEP_AGENT_TIMEOUT_SECONDS = int(os.getenv("DEEP_AGENT_TIMEOUT_SECONDS", "60"))
DEEP_AGENT_TEST_TIMEOUT_SECONDS = int(os.getenv("DEEP_AGENT_TEST_TIMEOUT_SECONDS", "15"))

# Test function to check if deep agent service is accessible
def test_deep_agent_connection() -> dict:
    """Test if the deep agent service is responding and find working endpoints"""
    try:
        print("\n[TEST] Testing deep agent service connection...")
        base_url = DEEP_AGENT_URL.replace('/deep-task', '')
        
        # Test the actual health endpoint. The service base URL can validly return 404.
        health_url = f"{base_url}/health"
        response = requests.get(health_url, timeout=DEEP_AGENT_TEST_TIMEOUT_SECONDS)
        print(f"[TEST] Health URL status: {response.status_code}")
        print(f"[TEST] Response: {response.text[:200]}")
        
        # Try common endpoints to find what works
        test_endpoints = [
            f"{base_url}/docs",
            f"{base_url}/health",
            f"{base_url}/api",
            f"{base_url}/api/health",
            f"{base_url}/deep-task",
            f"{base_url}/deep-research",
        ]
        
        working_endpoints = []
        for endpoint in test_endpoints:
            try:
                resp = requests.get(endpoint, timeout=8)
                if resp.status_code < 500:  # Not a server error
                    working_endpoints.append({
                        "endpoint": endpoint,
                        "status": resp.status_code,
                        "method": "GET",
                        "likely_valid": resp.status_code == 200
                    })
                    print(f"[TEST] {endpoint}: {resp.status_code}")
            except:
                pass
        
        # Also test /deep-task with POST (what we actually use)
        print(f"[TEST] Testing POST to /deep-task...")
        try:
            test_payload = {
                "query": "test",
                "user_id": "streamlit-ui",
                "conversation_id": "service-test",
            }
            post_response = requests.post(
                f"{base_url}/deep-task",
                json=test_payload,
                timeout=DEEP_AGENT_TEST_TIMEOUT_SECONDS
            )
            print(f"[TEST] POST /deep-task status: {post_response.status_code}")
            print(f"[TEST] POST response: {post_response.text[:500]}")
            
            # Try to parse response
            try:
                resp_json = post_response.json()
                print(f"[TEST] POST response JSON keys: {list(resp_json.keys()) if isinstance(resp_json, dict) else 'not a dict'}")
            except:
                pass
            
            working_endpoints.append({
                "endpoint": f"{base_url}/deep-task",
                "status": post_response.status_code,
                "method": "POST",
                "likely_valid": post_response.status_code in [200, 201],
                "note": "This is what we actually use",
                "response_sample": post_response.text[:200]
            })
        except Exception as e:
            print(f"[TEST] POST failed: {str(e)}")
        
        return {
            "status": "connected",
            "base_url": base_url,
            "code": response.status_code,
            "url": DEEP_AGENT_URL,
            "working_endpoints": working_endpoints,
            "message": "Service is reachable. Check endpoint list below."
        }
    except requests.exceptions.ConnectionError:
        print("[TEST] Connection refused - Service is down or wrong URL")
        return {
            "status": "connection_error",
            "url": DEEP_AGENT_URL,
            "error": "Cannot connect to service - service may be down or URL is incorrect"
        }
    except requests.exceptions.Timeout:
        print("[TEST] Timeout - Service not responding")
        return {
            "status": "timeout",
            "url": DEEP_AGENT_URL,
            "error": "Service timeout - response took too long"
        }
    except Exception as e:
        print(f"[TEST] Error: {str(e)}")
        return {
            "status": "error",
            "url": DEEP_AGENT_URL,
            "error": str(e)
        }

def requires_deep_research(query: str) -> bool:
    """Check if query requires deep research based on keywords"""
    keywords = [
        "deep research",
        "detailed report",
        "compare in detail",
        "step by step research",
        "comprehensive analysis",
        "in-depth study",
        "thorough investigation"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in keywords)


def call_deep_agent(query: str, status_callback=None) -> tuple:
    """
    Call the deep agent service for complex research tasks.
    Returns: (response_text, status_updates_list)
    status_callback: optional callable to track status updates in real-time
    """
    try:
        print(f"[DEEP AGENT] Calling deep agent service with query: {query}")
        
        statuses = []
        
        # Status update helper
        def update_status(status: str, substatus: str = ""):
            msg = f"{status}"
            if substatus:
                msg += f" - {substatus}"
            statuses.append({"timestamp": time.time(), "status": status, "substatus": substatus})
            print(f"[DEEP AGENT] {msg}")
            if status_callback:
                status_callback(msg)
        
        update_status("Initializing", "Connecting to deep agent service")
        
        payload = {
            "query": query,
            "user_id": "streamlit-ui",
            "conversation_id": f"thread-{int(time.time())}",
        }
        
        # Swagger exposes POST /deep-task with query, user_id, and conversation_id.
        base_url = DEEP_AGENT_URL.replace('/deep-task', '')
        endpoints = list(dict.fromkeys([DEEP_AGENT_URL, f"{base_url}/deep-task"]))
        
        update_status("Planning", "Analyzing query structure")
        
        for endpoint in endpoints:
            try:
                update_status("Connecting", f"Endpoint: {endpoint.split('/')[-1]}")
                print(f"\n[DEEP AGENT] Trying endpoint: {endpoint}")
                print(f"[DEEP AGENT] Payload keys: {list(payload.keys())}")
                
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=DEEP_AGENT_TIMEOUT_SECONDS
                )
                
                print(f"[DEEP AGENT] Response status: {response.status_code}")
                print(f"[DEEP AGENT] Response headers: {dict(response.headers)}")
                print(f"[DEEP AGENT] Response body: {response.text[:500]}")
                
                if response.status_code == 200:
                    update_status("Reasoning", "Processing research query")
                    result = response.json()
                    print(f"[DEEP AGENT] Success with endpoint: {endpoint}")
                    print(f"[DEEP AGENT] Result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                    
                    update_status("Searching", "Gathering information")
                    
                    # Handle different response formats
                    response_text = ""
                    if isinstance(result, dict):
                        if "response" in result:
                            response_text = result["response"]
                        elif "result" in result:
                            response_text = result["result"]
                        elif "message" in result:
                            response_text = result["message"]
                        elif "data" in result:
                            response_text = result["data"]
                        else:
                            response_text = json.dumps(result)
                    else:
                        response_text = str(result)
                    
                    if not response_text.strip():
                        print("[DEEP AGENT] Service returned an empty response")
                        update_status("Empty Response", "Trying again")
                        continue

                    # Only treat explicit service-level refusal as failure. Normal answers can mention
                    # "additional information", so do not use that phrase as a failure signal.
                    explicit_failure = (
                        "not able to execute" in response_text.lower()
                        or "unable to execute" in response_text.lower()
                        or response_text.lower().startswith("error:")
                    )
                    if explicit_failure:
                        print(f"[DEEP AGENT] Service returned error in response: {response_text}")
                        update_status("Service Response", "Trying again")
                        continue
                    
                    print(f"[DEEP AGENT] Response text length: {len(response_text)}")
                    update_status("Complete", "Research finished")
                    return response_text, statuses
                elif response.status_code == 404:
                    print(f"[DEEP AGENT] Endpoint not found (404): {endpoint}")
                    update_status("Not Found", f"Endpoint returned 404")
                    continue
                elif response.status_code == 405:
                    print(f"[DEEP AGENT] Method not allowed (405): {endpoint}")
                    update_status("Method Error", f"HTTP 405 - POST not allowed")
                    continue
                elif response.status_code == 500:
                    print(f"[DEEP AGENT] Server error (500): {response.text[:200]}")
                    update_status("Server Error", f"Remote service error")
                    continue
                elif response.status_code == 429:
                    print(f"[DEEP AGENT] Token/rate limit error (429): {response.text[:200]}")
                    update_status("Token Limit", "Remote model quota exceeded")
                    return (
                        "Token limit exceeded. Please come back tomorrow, or try again with a shorter question.",
                        statuses,
                    )
                elif response.status_code in (401, 403):
                    print(f"[DEEP AGENT] Auth error ({response.status_code}): {response.text[:200]}")
                    update_status("Auth Error", "Remote service credentials need attention")
                    return (
                        "The deep agent could not authenticate with one of its services. Please check deployment environment variables.",
                        statuses,
                    )
                else:
                    print(f"[DEEP AGENT] Error {response.status_code}: {response.text[:200]}")
                    update_status("Error", f"HTTP {response.status_code}")
                    continue
                        
            except requests.exceptions.Timeout:
                print(f"[DEEP AGENT] Timeout on {endpoint}")
                update_status("Timeout", f"Request took too long")
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"[DEEP AGENT] Connection error to {endpoint}: {str(e)}")
                update_status("Connection Failed", f"Cannot reach endpoint")
                continue
            except json.JSONDecodeError as e:
                print(f"[DEEP AGENT] Invalid JSON response: {str(e)}")
                update_status("Invalid Response", f"Response is not valid JSON")
                continue
            except Exception as e:
                print(f"[DEEP AGENT] Error with endpoint {endpoint}: {type(e).__name__}: {str(e)}")
                update_status("Error", f"Request failed: {type(e).__name__}")
                continue
        
        # If all endpoints fail, return error
        print("[DEEP AGENT] All endpoints failed")
        update_status("Failed", "Service unavailable")
        
        error_msg = (
            "Deep agent service unavailable. The service may be waking up, busy, "
            "or the request may need a different endpoint payload. Please wait a moment and try again."
        )
        return error_msg, statuses
        
    except Exception as e:
        print(f"[DEEP AGENT] Error calling deep agent: {str(e)}")
        if status_callback:
            status_callback(f"Error: {str(e)}")
        error_msg = f"Error calling deep research service: {str(e)}"
        return error_msg, []


# -------------------
# 4. Bind tools to LLM
# -------------------
tools = [tavily_tool, search_youtube_videos, generate_stability_image, serpapi_tool, calculator]
llm_with_tools = model.bind_tools(tools)


# -------------------
# 5. Chat graph setup
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def _truncate_text(value: object, limit: int = 260) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def _parse_tool_payload(content: object) -> object:
    if not isinstance(content, str):
        return content
    try:
        return json.loads(content)
    except Exception:
        return content


def _search_items_from_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("results", "organic_results", "news_results", "videos"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def _tool_result_fallback(messages: list[BaseMessage]) -> str:
    tool_messages = [message for message in messages if isinstance(message, ToolMessage)]
    if not tool_messages:
        return (
            "The model had trouble formatting a tool call. Please try rephrasing the request "
            "or asking for fewer results."
        )

    lines = [
        "I found results, but the model had trouble formatting the final tool response. Here are the best matches:"
    ]
    added = 0

    for tool_message in tool_messages[-3:]:
        payload = _parse_tool_payload(tool_message.content)
        for item in _search_items_from_payload(payload):
            title = item.get("title") or item.get("name") or item.get("source") or "Result"
            url = item.get("url") or item.get("link") or item.get("href")
            snippet = item.get("content") or item.get("snippet") or item.get("description") or ""

            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title}")

            if snippet:
                lines.append(f"  {_truncate_text(snippet, 220)}")

            added += 1
            if added >= 5:
                return "\n".join(lines)

    if added:
        return "\n".join(lines)

    latest_content = str(tool_messages[-1].content or "").strip()
    if latest_content:
        return (
            "The tool returned data, but the model had trouble formatting it cleanly.\n\n"
            f"```text\n{_truncate_text(latest_content, 1500)}\n```"
        )

    return (
        "The tool ran, but the model had trouble formatting the response. Please try again "
        "with a more specific prompt."
    )


def chat_node(state: ChatState) -> dict:
    try:
        print("===== CHAT NODE STARTED =====")

        print("Messages:", state["messages"])

        groq_key = os.getenv("GROQ_API_KEY")
        print("GROQ KEY EXISTS:", bool(groq_key))

        tavily_key = os.getenv("TAVILY_API_KEY")
        print("TAVILY KEY EXISTS:", bool(tavily_key))

        # Extract the latest user message
        latest_message = state["messages"][-1]
        if isinstance(latest_message, HumanMessage):
            user_query = latest_message.content
            print(f"[CHAT NODE] User query: {user_query}")
            
            # Check if query requires deep research
            if requires_deep_research(user_query):
                print("[CHAT NODE] Deep research detected - routing to deep agent")
                deep_response, statuses = call_deep_agent(user_query)
                print(f"[CHAT NODE] Deep agent response received with {len(statuses)} status updates")
                
                # Create message list with status updates
                response_messages = []
                
                # Add status messages
                if statuses:
                    status_text = "**Deep Research Progress:**\n"
                    for status_update in statuses:
                        status_text += f"- {status_update['status']}"
                        if status_update['substatus']:
                            status_text += f" - {status_update['substatus']}"
                        status_text += "\n"
                    response_messages.append(AIMessage(content=status_text, metadata={"type": "status"}))
                
                # Add final response
                response_messages.append(AIMessage(content=deep_response))
                
                return {"messages": response_messages}

        print("===== BEFORE LLM INVOKE =====")

        response = llm_with_tools.invoke(state["messages"])

        print("===== AFTER LLM INVOKE =====")
        print(response)

        return {"messages": [response]}

    except Exception as e:
        print("===== ERROR IN CHAT NODE =====")
        error_text = str(e)
        print(error_text)

        if "failed_generation" in error_text.lower() or "failed to call a function" in error_text.lower():
            return {
                "messages": [
                    AIMessage(content=_tool_result_fallback(state["messages"]))
                ]
            }

        return {
            "messages": [
                AIMessage(content="Error: The agent could not complete that response. Please try again in a moment.")
            ]
        }

tool_node = ToolNode(tools)

# SQLite checkpointer for persistence
# SQLite checkpointer for persistence
conn = sqlite3.connect(database='chatbot.db3', check_same_thread=False)

# Create cursor
cursor = conn.cursor()

# Create checkpoints table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT
)
""")

# Save changes
conn.commit()

# Initialize LangGraph checkpointer
checkpointer = SqliteSaver(conn=conn)


graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)


graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge('tools', 'chat_node')


chatbot = graph.compile(checkpointer=checkpointer)

# 
# -------------------
# 6. Helper to list threads
# -------------------
def retrieve_all_threads():
    all_threads = set()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        for row in rows:
            all_threads.add(row)
    return list(all_threads)


def get_latest_news():
    api_key = "Ya5b4563c7e4244508c554840b6186921"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [(a["title"], a["url"]) for a in articles[:10]]
    return []
