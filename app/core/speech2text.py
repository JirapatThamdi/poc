from openai import OpenAI

class SpeechToTextService:
    def get_schema(self):
        """
        Schema for OpenAI Function Calling
        """
        return {
            "type": "function",
            "name": "speech2text",
            "description": "Transcribe audio from a given audio file into text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_file": {
                        "type": "string",
                        "description": "The audio file to transcribe."
                    }
                }
            },
            "required": ["audio_file"]
        }
    
    async def call(self, audio_file, client: OpenAI):
        """
        Call the OpenAI API to transcribe audio to text.
        
        :param audio_file: The audio file to transcribe.
        :param client: An instance of OpenAI client.
        
        :return: The transcribed text.
        """
            
        try:
            # If the provided audio is bytes, save it to a temporary file
            if isinstance(audio_file, bytes):
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.m4a', mode="wb") as temp_file:
                    temp_file.write(audio_file)
                    audio_file = temp_file.name
                    
            with open(audio_file, "rb") as file:
                stream = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=file,
                    response_format="text",
                    stream=True
                )
                
                if not stream:
                    raise ValueError("No stream returned from OpenAI API")
                
                for event in stream:
                    if event.type == "transcript.text.done":
                        return event.text
                
                raise ValueError("Transcription failed or no text returned.")
        finally:
            # Clean up the temporary file if it was created
            if isinstance(audio_file, str) and audio_file.endswith('.m4a'):
                import os
                os.remove(audio_file)