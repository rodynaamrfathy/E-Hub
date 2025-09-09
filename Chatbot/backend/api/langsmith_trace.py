from langsmith.run_helpers import traceable

@traceable(name="send_message_stream")
async def event_generator_with_trace(conv_id, content, image_paths, chatbot, msg_service, db, temp_files):
    try:
        run_name = f"Conversation-{conv_id}"
        full_response_tokens = []

        # Trace the streaming interaction
        with client.trace(run_name, inputs={"content": content, "images": image_paths}) as run:
            async for token in chatbot.stream_response(content, image_paths if image_paths else None):
                full_response_tokens.append(token.strip())
                # send partial response
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0)

            # Get full response
            full_response = chatbot.get_full_response() or " ".join(full_response_tokens).strip()

            # Save message in DB
            if full_response:
                ai_msg = await msg_service.create_message(
                    db, conv_id, sender="assistant", content=full_response
                )

            # Mark run outputs
            run.end(outputs={"response": full_response})
            yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        raise
    finally:
        for path in temp_files:
            if os.path.exists(path):
                os.unlink(path)
