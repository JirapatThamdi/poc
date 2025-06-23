from app.core.speech2text import SpeechToTextService

class ServiceManager:
    def __init__(self):
        self.services = {
            "speech2text": SpeechToTextService()
        }
    
    def get_service(self):
        """
        Get a service by name. (to be used in OpenAI Function Calling)

        :param service_name: The name of the service to retrieve.
        :return: The service instance if found, otherwise None.
        """
        return [self.services[service_name].get_schema() for service_name in self.services]
    
    async def call(self, service_name: str, *args, **kwargs):
        """
        Call a service by name with the provided arguments.

        :param service_name: The name of the service to call.
        :param args: Positional arguments for the service call.
        :param kwargs: Keyword arguments for the service call.
        :return: The result of the service call.
        """
        if service_name in self.services:
            return await self.services[service_name].call(*args, **kwargs)
        else:
            raise ValueError(f"Service '{service_name}' not found.")