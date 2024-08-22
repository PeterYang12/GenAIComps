# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

from fastapi.responses import StreamingResponse
from langchain_community.llms import VLLMOpenAI
from langchain_core.prompts import PromptTemplate
from openai import OpenAI

from comps import (
    CustomLogger,
    GeneratedDoc,
    LLMParamsDoc,
    ServiceType,
    opea_microservices,
    opea_telemetry,
    register_microservice,
)

from comps.cores.proto.api_protocol import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionStreamResponse

logger = CustomLogger("llm_vllm")
logflag = os.getenv("LOGFLAG", False)


@opea_telemetry
def post_process_text(text: str):
    if text == " ":
        return "data: @#$\n\n"
    if text == "\n":
        return "data: <br/>\n\n"
    if text.isspace():
        return None
    new_text = text.replace(" ", "@#$")
    return f"data: {new_text}\n\n"


@register_microservice(
    name="opea_service@llm_vllm",
    service_type=ServiceType.LLM,
    endpoint="/v1/chat/completions",
    host="0.0.0.0",
    port=9000,
)
def llm_generate(input: ChatCompletionRequest):
    print(input)
    if logflag:
        logger.info(input)
    llm_endpoint = os.getenv("vLLM_ENDPOINT", "http://localhost:8008")
    # model_name = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    
    prompt_template = None
    if input.chat_template:
        prompt_template = PromptTemplate.from_template(input.chat_template)
        input_variables = prompt_template.input_variables

    client = OpenAI(
        api_key="EMPTY",
        base_url=llm_endpoint + "/v1",
    )


    chat_completion = client.chat.completions.create(
        model="Intel/neural-chat-7b-v3-3",
        messages=input.messages,
    )

    if input.stream:
        def stream_generator():
            for c in chat_completion:
                if logflag:
                    logger.info(c)
                yield f"data: {c.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        if logflag:
            logger.info(chat_completion)
        return chat_completion

#################################################


    # llm = VLLMOpenAI(
    #     openai_api_key="EMPTY",
    #     openai_api_base=llm_endpoint + "/v1",
    #     max_tokens=input.max_new_tokens,
    #     model_name=model_name,
    #     top_p=input.top_p,
    #     temperature=input.temperature,
    #     streaming=input.streaming,
    # )

    # if input.streaming:

    #     def stream_generator():
    #         chat_response = ""
    #         for text in llm.stream(input.query):
    #             chat_response += text
    #             chunk_repr = repr(text.encode("utf-8"))
    #             yield f"data: {chunk_repr}\n\n"
    #         if logflag:
    #             logger.info(f"[llm - chat_stream] stream response: {chat_response}")
    #         yield "data: [DONE]\n\n"

    #     return StreamingResponse(stream_generator(), media_type="text/event-stream")
    # else:
    #     response = llm.invoke(input.query)
    #     if logflag:
    #         logger.info(response)
    #     return GeneratedDoc(text=response, prompt=input.query)


if __name__ == "__main__":
    opea_microservices["opea_service@llm_vllm"].start()
