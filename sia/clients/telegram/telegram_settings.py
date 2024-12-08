class SiaTelegramSettings:
    
    def __init__(self, sia):
        self.sia = sia

    def get_settings(self):
        return self.sia.character.platform_settings.get("telegram", {})
