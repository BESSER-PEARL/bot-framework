from besser.bot.core.processors.processor import Processor
from besser.bot.nlp.llm.llm import LLM
from besser.bot.core.bot import Bot
from besser.bot.core.session import Session
from besser.bot.nlp.nlp_engine import NLPEngine


class UserAdaptationProcessor(Processor):
    """The UserAdaptationProcessor takes into account the user's profile and adapts the bot's responses to fit the 
    profile. The goal is to increase the user experience.

    This processor leverages LLMs to adapt the messages given a user profile. For static profiles, an adaptation will be 
    done once. If the profile changes, then an adapation will be triggered again.

    Args:
        user_messages (bool): Whether the processor should be applied to user messages.
        bot_messages (bool): Whether the processor should be applied to bot messages.
        llm_name (str): the name of the LLM to use.
        context (str): additional context to improve the adaptation. should include information about the bot itself and the task it should accomplish

    Attributes:
        user_messages (bool): Whether the processor should be applied to user messages.
        bot_messages (bool): Whether the processor should be applied to bot messages.
        llm_name (str): the name of the LLM to use.
        context (str): additional context to improve the adaptation. should include information about the bot itself and the task it should accomplish        
    """
    def __init__(self, bot: 'Bot', llm_name: str, context: str = None):
        super().__init__(bot_messages=True)
        self._llm_name: str = llm_name
        self._nlp_engine: 'NLPEngine' = bot.nlp_engine
        # does it make sense to have a constructor param for context? It essentially does the same as the global_context attr of LLMs. 
        # The only reason I added it here is to have a default context 'You are a chatbot' but I could just as well add it to the usre context?
        if context:
            self._context = context
        else:
            self._context = "You are a chatbot."

# add capability to improve/change prompt of context
    def process(self, session: 'Session', message: str) -> str:
        llm: LLM = self._nlp_engine._llms[self._llm_name]
        prompt = f"You need to adapt this message: {message}\n Only respond with the adapated message!"
        llm_response: str = llm.predict(prompt, session=session)
        return llm_response

    def add_user_model(self, session: 'Session', user_model: dict) -> None:
        user_context = f"You are capable of adapting your predefined answers based on a given user profile.\
                Your goal is to increase the user experience by adapting the messages based on the different attributes of the user \
                profile as best as possible and take all the attributes into account.\
                You are free to adapt the messages in any way you like.\
                    The user should relate more. This is the user's profile\n\
                    {str(user_model)}\n"
        self._nlp_engine._llms[self._llm_name].add_user_context(context=self._context + user_context, session=session)
