version = '0.5.0'
game = f'V{version} | >h'
env = 'dev'

tdb_settings = dict(
    credentials=dict(
        discord=dict(
            token='NDg4NjY5NTEwNTU1OTI2NTM5.Dnfl5A.kw_JWEKe-vuEf0KSYmA1vGCqUL8',
        )
    ),
    database=dict(
        dev=dict(
            type='sqlite3',
            database_name='tdr.sqlite3',
            username=None,
            password=None,
            database=None,
            location='C:\\Users\\Administrator\\Desktop\\TDR\\TDR\\',  # Server windows
        ),
        prod=dict(
            type='sqlite3',
            database_name='tdr.sqlite3',
            username=None,
            password=None,
            database=None,
            location='C:\\Users\\Administrator\\Desktop\\TDR\\TDR\\'  # Server
        )
    ),
    queue=dict(
        host='rabbitmq.glg-solutions.ovh',
        username='tdb',
        password='SuperAwesomeUnhackablePassword123',
        virtualhost='tdb'
    ),
    prefixes=[
    #    'tdb!',
        '>'
    ]
)

bot_credentials = tdb_settings['credentials']['discord']
rabbitmq_settings = tdb_settings['queue']

allowed_servers = dict(
    tdr=dict(
        name='The Dark Room',
        invite_link='https://discord.gg/DhPnfUv',
    )
)

bot_servers = dict(
    tdr=dict(
        connect_on_start=True,
        debug_mode=dict(
            status=True,
            channel='#bot-testingground'
        )
    )
)

database_settings = tdb_settings['database'][env]

embed_color = 0x400a6b

assets = dict(
    kissing=[
        'assets/kiss/1.gif',
        'assets/kiss/2.gif',
        'assets/kiss/3.gif',
        'assets/kiss/4.gif',
    ],
    fucking=[
        'assets/fuck/1.gif',
        'assets/fuck/2.gif',
        'assets/fuck/3.gif',
        'assets/fuck/4.gif',
        'assets/fuck/5.gif',
        'assets/fuck/6.gif',
    ]
)
rules = dict(
    about='This server is made without any moderators or administrators, we have members of a table, this table can be seen as the round table from the king Arthur story, we are all equal and big decisions are made by us all.',
    general=[
        'If you get caught as an catfish, you will immediately be banned!',
        'Do not backtalk to staff, if you dont agree with something an staff does, then dm someone higher.',
        'Have some common sense.',
        'Do not harrass, this also incudes continuing with a "joke" when someone asked or told you to not.',
        'Do not slut shame.',
        'Play nicely or get punished.',
        'Bot abuse in channels other than bot-commands and|or no-rules',
        'Do not dm someone with a "DO NOT DM" role, if they have a "Ask for dm" then ask before you dm.',
        'Most channels are opened upon gaining the "18+" role, we suggest you verify.',
        'If you are incapable of handeling lewd and thirst, then we advice you to leave.',
        'The server is going to be 18+, for now its free for 13+ (discord tos requires you to be 13 or older)',
    ],
    verification=dict(
        adult=dict(
            title='How to get verified as 18+',
            message='To get verified all you have to do is: send a dm to any of the members of The Table with: a picture of some form of identification and yourself.',
        ),
        gender=dict(
            title='How to get verified as Male or Female',
            message='To get verified as a (fe)male, you have to send a picture of yourself (may be lewd) where your face is clearly visible and holding a sign stating the date, the server and your tag on it.',
        )
    )
)

TYPES = dict(
    GENERAL=1,
    STAFF=10,
    ADMIN=100
)

rules_kitty = [
    'Rule 1. You can say whatever you want in the General just don\'t be rude, spam or post links in there, And or roleplaying, It is only for talking',
    'Rule 2. Do Not Just Randomly Talk In The #Prayer-request, If You Would Like To use It For It\'s Purpose Please Feel Free To Do So, And We Will Hopefully Make Your Day Better.',
    'Rule 3. Do Not Talk In #Role-Request Unless You Want A Role Then Just Simply Put What You Want And We Will Get You That Role.',
    'Rule 4. Pictures and videos go into <#487909042744721409>, Don\'t post selfie\'s and art work in there. Go to <#500787631165145098> and <#489537775390031882> for that.',
    'Rule 5. Do not judge anyone for posting a nude or a tease, As we will take that as slut shaming.',
    'Rule 6. The Word Fag and Faggot are banned, Along with the N word, If you use it you will be warned by the bot.',
]

rules_kitty_extended = [
    'Rule 7. If you need anything and i am not online, You can always just ping one of the pro owners, The ones i suggest since they are online a lot are <@392338765684670464> and <@340956641723678720>, Or you can just wait till i become online.'	
    'Rule 8. No Roleplaying outside of a roleplaying room, And keep All NSFW stuff in the NSFW channels. To see NSFW channels go to <#492719514098860032> and get the role NSFW.',
    'Rule 9. If a fight breaks out we will warn you to stop if you do not you will be muted for 3 minutes, And if you continue after those 3 minutes you will be muted again and for longer.',
    'Rule 10. Do not swear a lot, As all ages of people could possibly be in this server so please somewhat keep it PG with the swearing.',
    'Rule 11. Keep all Bot Commands in <#500286338084503562>!',
    'Rule 12. If you get caught as an catfish, you will immediately be banned!'
    'Rule 13. And with all of that said, Please be respectful and kind to everyone in the server!',
    'Thank you for reading the <#486802370559475712> <3'
]