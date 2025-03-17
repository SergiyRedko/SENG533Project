class FormattedReply:
    def __init__(self):
        """
        Initialize a FormattedReply instance.

        Attributes:
          done_reason (str): The reason the generation ended.
          done (bool): Whether the generation is complete.
          duration (float): Total processing duration in seconds.
          eval_duration (float): Duration spent in evaluation in seconds.
          response (str): The model's output with '/' characters removed.
          model (str): The model used.
          query (str): The query sent to the model.
        """
        self.done_reason = "unknown"
        self.done = False
        self.duration = -1
        self.eval_duration = -1
        self.response = "NO RESPONSE"
        self.model = ""
        self.query = ""
        self.load_duration = -1

    @classmethod
    def decompose_ollama_reply(cls, reply):
        """
        Creates a FormattedReply instance from a reply object.

        Parameters:
          reply: An object with attributes `done`, `done_reason`, `total_duration`,
                 `prompt_eval_duration`, and `response`.

        Returns:
          An instance of FormattedReply with fields set from the reply object.
        """
        instance = cls()
        instance.done = reply.done
        instance.done_reason = reply.done_reason
        instance.duration = reply.total_duration / 1000000000
        instance.eval_duration = reply.prompt_eval_duration / 1000000000
        instance.response = reply.response
        instance.load_duration = reply.load_duration

        return instance
