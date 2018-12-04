import discord
import config
from models.DB import DB
from models.Command import Command


class Nhie(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        d_q = DB().fetch_one('SELECT * FROM nhie_questions LIMIT ? offset abs(random()) % (select count(*) from nhie_questions) + 1', (1,))
        d_id, d_question = d_q

        embed = discord.Embed(title='Never Have i Ever', description='', color=config.embed_color, colour=config.embed_color)
        embed.add_field(name='Question:', value=d_question, inline=False)

        return await self.message.channel.send(embed=embed)


if __name__ == "__main__":
    import requests
    from bs4 import BeautifulSoup
    request = requests.get('https://neverhaveever.com/tag/dirty/')
    nhie_site = request.text
    soup = BeautifulSoup(nhie_site, 'html.parser')

    list = soup.find(id='dirty-questions')
    questions = []
    for item in list.find_all('li'):
        questions.append((item.get_text(),))
    DB().execute_many('INSERT INTO nhie_questions(question) VALUES(?)', questions)
