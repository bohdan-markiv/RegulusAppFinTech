import openai
import datetime
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GenerateResponse:
    def __init__(self, prompt, secret, thread_id, assistant_id, file):
        self.prompt = prompt
        self.messages = ""
        self.secret = secret
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.file = file

    def generate_input_message(self):
        return {
            "M": {"sender": {
                "S": "user"
            },
                "timestamp": {
                "S": str(datetime.datetime.now())
            },
                "text": {
                "S": self.prompt
            }}
        }

    def get_response_from_openai(self):
        OPENAI_API_KEY = self.secret

        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        if not self.assistant_id:
            assistant = client.beta.assistants.create(
                name="regulus_ai",
                description="You are the assistant which is supposed to help users get insights about the sustainable policies, green regulations, carbon offset markets, renewable energy mortgages, and subsidies for renewable energy projects.",
                instructions="Please, act as a platform Regulus AI. Refer to the user as to a compliance officer. Avoid informalities, jokes, and any other casual communication. Maintain a professional tone at all times and keep the conversation strictly focused on green policies and compliance matters. This is your principle of work - Regulus AI is an advanced platform that provides additional assistance to finance employees by automating the scanning and assessment processes. It stays continuously updated with the latest policies and legislation, ensuring Regulus AI can provide consulting on both current regulations and those soon to be introduced. This real-time updating capability allows Regulus AI to deliver relevant compliance guidance, keeping your operations aligned with the fast-paced regulatory field. Simply ask a question or upload a document to the simple and intuitive chatbot and receive a thorough compliance analysis instantly. This service not only answers questions regarding the latest regulatory updates and optimizes the time spent scanning websites, but also analyzes existing documents, directives, and project descriptions to ensure they are fully compliant with current policies.",
                model="gpt-3.5-turbo",
                tools=[
                    {"type": "code_interpreter"},
                    {"type": "file_search"}  # Add file search tool
                ],
            )
            self.assistant_id = assistant.id

        # Might also be a good idea to put it in dotenv or secret manager
        # assistant_id = "asst_Y0qzswFxWcZXZ07XG3CVNC7V"
        if not self.thread_id:
            # Step 2: Create a Thread
            thread = client.beta.threads.create()
            self.thread_id = thread.id

        if self.file["id"]:
            attachments = [{
                "file_id": self.file["id"],
                "tools": [{"type": "file_search"}]}]
            self.prompt = f"{self.prompt} - {
                self.file["name"]}"
        else:
            attachments = []
        logger.info(f"prompt - {self.prompt}")
        logger.info("assistant and thread are initiated")
        logger.info(f"Attachment - {attachments}")

        message = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=self.prompt,
            attachments=attachments
        )

        logger.info("message have been created")
        # Step 4: Create a Run
        run = client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions="Please, act as a platform Regulus AI. Refer to the user as to a compliance officer."
        )

        logger.info("run has been created")
        if run.status == 'completed':
            self.messages = client.beta.threads.messages.list(
                thread_id=self.thread_id).data[0].content[0].text.value
        else:
            raise ("Error getting response from openai.")
        return {
            "M": {"sender": {
                "S": "bot"
            },
                "timestamp": {
                "S": str(datetime.datetime.now())
            },
                "text": {
                "S": self.messages}}
        }
