from langchain_openai import ChatOpenAI
import openai

def  test_langchain():
    api_key="MGNjNTlmNzQtNWZmYS0xMWYwLTkyMjEtYTZiNmQzNTVjYTA5OjNiYzcwNWZlLTQ3YzMtNGQ3My1iZmE3LWFkMTVhNjZlNTliOQ=="
    llm = ChatOpenAI(
        model="gauss2.2-37b",
        base_url="https://inference-webtrial-api.shuttle.sr-cloud.com/gauss2-2-37b-instruct/v1",
        api_key="MGNjNTlmNzQtNWZmYS0xMWYwLTkyMjEtYTZiNmQzNTVjYTA5OjNiYzcwNWZlLTQ3YzMtNGQ3My1iZmE3LWFkMTVhNjZlNTliOQ==", 
        default_headers={
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json",
            "accept": "*/*"
        },

    )

    messages = [
        ("user", "Write 3 sentences that start with SAMSUNG."),
    ]
    print(messages)
    print(llm.invoke(messages))

def test_openai():
    api_key="MGNjNTlmNzQtNWZmYS0xMWYwLTkyMjEtYTZiNmQzNTVjYTA5OjNiYzcwNWZlLTQ3YzMtNGQ3My1iZmE3LWFkMTVhNjZlNTliOQ=="
    client = openai.OpenAI(
        base_url="https://inference-webtrial-api.shuttle.sr-cloud.com/gauss2-2-37b-instruct/v1",
        api_key="MGNjNTlmNzQtNWZmYS0xMWYwLTkyMjEtYTZiNmQzNTVjYTA5OjNiYzcwNWZlLTQ3YzMtNGQ3My1iZmE3LWFkMTVhNjZlNTliOQ==", 
        default_headers={
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json",
            "accept": "*/*"
        },
    )

    messages = [
        {"role": "user", "content": "Write 3 sentences that start with SAMSUNG."},
    ]

    assistant_response_content = ""    

    with client.chat.completions.create(
        model="gauss2.2-37b",
        messages=messages,
        stream=True
    ) as stream:
        for chunk in stream:
            if chunk.choices[0].delta and chunk.choices[0].delta.content:
                # Accumulate the content only if it's not None
                assistant_response_content += chunk.choices[0].delta.content
                # yield f"data: {chunk.choices[0].delta.content}\n\n"
            if chunk.choices[0].finish_reason == "stop":
                break  # Stop if the finish reason is 'stop'

    print(assistant_response_content)

if __name__ == "__main__":
    test_openai()
