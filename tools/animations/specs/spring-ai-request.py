import sys
from animlib import Anim

a = Anim("pb-ai", "One <code>ChatClient</code> call — memory, the tool loop and RAG in advisor order",
         "Spring AI advisor chain",
         "A ChatClient request flows through MessageChatMemoryAdvisor, the auto-registered ToolCallingAdvisor and "
         "QuestionAnswerAdvisor to the ChatModel, and the response flows back the same way. Memory loads and saves the "
         "conversation, RAG adds context from the vector store, and when the model returns a tool call the "
         "ToolCallingAdvisor runs the @Tool method and calls the model again.", 800, 356, top=56)

a.box("app", 16, 86, 110, 70, "your code", ["chat.prompt()", ".call()"], sub_mono=True)
a.box("mem", 146, 86, 130, 70, "MessageChatMemory", extra=[("Advisor", "t-b t-11"), ("order +200", "t-xs t-sub t-mono")], title_cls="t-11")
a.box("tool", 296, 86, 130, 70, "ToolCalling", extra=[("Advisor", "t-b t-11"), ("+300 · auto", "t-xs t-sub t-mono")], title_cls="t-11")
a.box("rag", 446, 86, 130, 70, "QuestionAnswer", extra=[("Advisor", "t-b t-11"), ("order 0", "t-xs t-sub t-mono")], title_cls="t-11")
a.box("model", 626, 86, 158, 70, "ChatModel", ["the LLM"], kind="band")
a.box("store", 146, 214, 130, 58, "ChatMemory", ["conversation history"])
a.box("toolm", 296, 214, 130, 58, "@Tool method", ["getOrderStatus(…)"], sub_mono=True, title_cls="t-mono")
a.box("vector", 446, 214, 130, 58, "VectorStore", ["policies · product facts"])

a.route("a2m", [(126, 121), (146, 121)])
a.route("m2t", [(276, 121), (296, 121)])
a.route("t2r", [(426, 121), (446, 121)])
a.route("r2l", [(576, 121), (626, 121)])
a.route("m2s", [(211, 156), (211, 214)])
a.route("t2tool", [(361, 156), (361, 214)])
a.route("r2v", [(511, 156), (511, 214)])

a.panel(16, 290, 768, 58)
a.chip("prompt", 28, 303, 330, "Prompt now has", {
    "q": ("the question", "none"), "hist": ("+ history", "active"), "tools": ("+ history + tool schemas", "active"),
    "rag": ("+ history, tools, context", "committed"), "res": ("… + tool result", "committed")})
a.chip("calls", 370, 303, 170, "Model calls", {"one": ("1", "active"), "two": ("2", "committed")})
a.chip("answer", 552, 303, 220, "Answer", {"tool": ("tool call", "suspended"), "text": ("text ✓", "committed")})

a.scene("rag", "1 · Memory + RAG", [
    {"path": "a2m", "hl": "app mem", "tx": {"prompt": "q"}, "text": "<code>chat.prompt().user(\"Can I return fresh produce?\").call()</code> builds a <code>ChatClientRequest</code>, which passes through the advisors in order, <strong>lowest order first</strong>."},
    {"path": "m2s", "hl": "store", "tx": {"prompt": "hist"}, "text": "<code>MessageChatMemoryAdvisor</code> loads this conversation's history from <code>ChatMemory</code> and adds it as messages."},
    {"path": "m2s:rev,m2t", "hl": "tool", "tx": {"prompt": "tools"}, "text": "<code>ToolCallingAdvisor</code> (auto-registered) adds the schemas of the available <code>@Tool</code> methods. Everything after it runs <em>inside</em> the tool-calling loop."},
    {"path": "t2r,r2v", "hl": "vector", "tx": {"prompt": "rag"}, "text": "<code>QuestionAnswerAdvisor</code> searches the vector store for chunks similar to the question, filtered per tenant, and adds them as context."},
    {"path": "r2v:rev,r2l", "hl": "model", "tx": {"calls": "one"}, "text": "The augmented prompt reaches the <code>ChatModel</code>."},
    {"path": "r2l:rev,t2r:rev", "hl": "tool", "tx": {"answer": "text"}, "text": "The model answers in text, with no tool call, so the loop ends after <strong>one</strong> model call."},
    {"path": "m2t:rev,m2s", "hl": "mem store", "text": "On the way out, the memory advisor saves the new user message and the answer to the conversation."},
    {"path": "m2s:rev,a2m:rev", "hl": "app", "text": "Your code gets the answer. Every advisor saw the request on the way in and the response on the way out, in reverse order."},
])

a.scene("tools", "2 · A tool call", [
    {"path": "a2m,m2t,t2r,r2l", "hl": "model", "tx": {"prompt": "rag", "calls": "one"}, "text": "<em>\"Where is my order 1042?\"</em> takes the same path: history, tool schemas and policy context, then the model."},
    {"path": "r2l:rev,t2r:rev", "token": "signal", "hl": "tool", "tx": {"answer": "tool"}, "text": "The model doesn't answer. It returns a <strong>tool call</strong>: <code>getOrderStatus({\"orderId\":\"1042\"})</code>."},
    {"path": "t2tool", "token": "signal", "hl": "toolm", "text": "<code>ToolCallingAdvisor</code> runs your <code>@Tool</code> method with those arguments plus a <code>ToolContext</code>: server-side data such as the customer id, which never comes from the model."},
    {"path": "t2tool:rev", "hl": "tool", "tx": {"prompt": "res"}, "text": "The method returns <code>{\"status\":\"SHIPPED\",\"eta\":\"2026-11-06\"}</code>, which is added to the conversation."},
    {"path": "t2r,r2l", "hl": "rag model", "tx": {"calls": "two"}, "text": "The loop calls the model <strong>again</strong>. Because the loop runs inside the advisor chain, advisors after it (RAG, logging) run on every iteration."},
    {"path": "r2l:rev,t2r:rev,m2t:rev,a2m:rev", "hl": "app", "tx": {"answer": "text"}, "text": "Now the model answers: <em>\"Your order shipped and arrives on 6 November.\"</em> Per-turn limits stop runaway loops (by default 40 calls per tool and 150 in total, §9.8)."},
])

a.write(sys.argv[1])
