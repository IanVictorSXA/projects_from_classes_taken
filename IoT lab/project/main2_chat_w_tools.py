# LLM chat with tools (from tools.py) - Agentic AI

from ollama import chat
import tools
import speak
import access_manager

def call_func(call, functions):
        """Run function called by the LLM and returns dictionary showing functions output
        
            Args:
                call : LLM's tool call (response.message.tool_calls[0])
                functions: dictionary of available functions. Keys are the name of the function. Values are function objects
                
            Returns: dictionary with role, tool name, and tool's output"""
        result = functions[call.function.name](**call.function.arguments)

        return {"role": "tool", "tool_name": call.function.name, "content": result}

        
def chat_w_tools(model : str, functions : dict, prompt : str, think : bool=True):
    """"Run LLM with tools
    
        Args:
            model: name of the model
            functions: dictionary of functions available for the model to use. Keys are name of the function. Value is the function object
            prompt: user's input
            
        Returns LLM's answer"""
    tools = list(functions.values())
    messages = [{"role": "user", "content": prompt}]
    
    response = chat(model=model, messages=messages, tools=tools, think=think)
    messages.append(response.message) 

    # If model wants to use a tool (Model can only call a single tool at a time in this implementation)
    if response.message.tool_calls:
        call = response.message.tool_calls[0]
        output = call_func(call, functions)

        messages.append(output) 

        final_response = chat(model=model, messages=messages, tools=tools, think=False) # print LLM's second asnwer when using tools
    else:
            # if there is not need for tools, print LLM's first answer
            final_response = response

    return final_response.message.content

volume = 0.19
song_volume = 0.06
tools.player.volume(song_volume)
model = "qwen3:0.6b"

# Run LLM chat until CTRL-C, then close mixer
try:
    access_manager.detect_person(volume)
    speak.speak_no_file(f"Access granted to SLM. " + "Please enter your prompt", volume)
    while True:
        message = chat_w_tools(model, tools.functions, input(">>> "), think=False)
        print(message)
        speak.speak_no_file(message, volume)

except KeyboardInterrupt as e:
     print(e)

finally:
     tools.player.close_mixer()
