import discord


class WrestlingCog:
    def __init__(self, bot):
        self.bot = bot
        self.classes = [
            'technician',
            'powerhouse',
            'giant',
            'cruiser',
            'striker'
        ]
        self.base_stats = dict(
            technician=dict(
                strength=42,
                reversal=70,
                offensive=dict(
                    punching=55,
                    kicking=58,
                    grapple=69,
                    objects=42,
                ),
                defensive=dict(
                    punching=53,
                    kicking=58,
                    grapple=62,
                    objects=61,
                ),
                total=570
            ),
            powerhouse=dict(
                strength=70,
                reversal=50,
                offensive=dict(
                    punching=82,
                    kicking=58,
                    grapple=60,
                    objects=40,
                ),
                defensive=dict(
                    punching=50,
                    kicking=58,
                    grapple=62,
                    objects=60,
                ),
                total=590
            ),
        )
