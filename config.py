version = '0.4.4'
game = 'V%s | tdb!commands' % version

bot_credentials = dict(
    token='NDg4NjY5NTEwNTU1OTI2NTM5.Dnfl5A.kw_JWEKe-vuEf0KSYmA1vGCqUL8',
)

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

database_settings = dict(
    type='sqlite3',
    database_name='tdr.sqlite3',
    username=None,
    password=None,
    database=None,
    location='C:\\Users\\Administrator\\Desktop\\TDR\\TDR\\'  # Server
    #location='D:\\TDR\\',  # Werk laptop
    #location='F:\\TDR\\',  # Home laptop
)

embed_color = 0x400a6b

rules = dict(
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
        'The server is currently for 16+ (exceptions are made for 15 year olds)',
    ],
    verification=dict(
        adult=dict(
            title='How to get verified as 18+',
            message='To get verified all you have to do is: send a dm to anyone in the Overlord role with: a picture of some form of identification and yourself.',
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

plugins = [
    dict(
        name='nickname',
        information=[
            'The nicname command allows you to set or chang your nickname',
            'each nickname would have to be verified by an staffmember,',
            'if your nickname has been approved of, then you will be notified and your nickname would change',
            '',
            'Usage: tdb!nickname {new nickname}',
            'Example: tdb!nickname "The awesomest bot"'
        ],
        command='tdb!nickname',
        usage='tdb!nickname {new nickname}',
        required_plugins=['poll'],
        type=TYPES['GENERAL']
    )
]

# rules_embi = [
#     'Rule #1. Don\'t disrespect each other or you\'ll be banned or kicked.',
#     'Rule #2. Don\'t join the voice chat"gaming bullshit" when you are not playing a game with someone else.',
#     'Rule #3. Do not spam or bother others user with Poke and messages. (Channel hopping is also spam!)',
#     'Rule #4. Don\'t post someone\'s personal information without their permission.',
#     'Rule #7. No suicide or self harm jokes or you\'ll be banned or kicked immediately.',
#     'Rule #8. Swearing is allowed as long as it doesn\'t harm another member.',
#     'Rule #9. No earrape or high pitched noise in voicechats.(Lola for example)',
# ]
#
# rules_embi_extended = [
#     'Rule #10. If someone is new in the server please welcome them with love.',
#     'Rule #11. Don\'t copy any nicknames.',
#     'Rule #12. If you have problems(at home, at school, with yourselves, depression, anxiety or whatever)you can always talk to me hmu',
#     'Rule #13. Do not link NSFW (sexual, racist, violent, disturbing or inappropriate content).',
#     'Rule #14. This is an English speaking and based server.',
#     'Rule #15. Dutch is allowed in: #nederlands🇳🇱',
#     'Rule #16. No begging for roles.',
#     'Rule #17. Don\'t cause drama (complaining about the server is seen as causing drama), you’ll not achieve anything by doing this. Dm me if you think a change is required.',
#     'Rule #18: If someone is using a music bot and you want to listen to something else, use one of the other bots in one of the other channel, we have 3 of them.'
# ]

rules_kitty = [
    'Make sure if you have anything to talk about or post it goes in the right channel.',
    'Please respect others and be kind as always!',
    'You can say whatever you want in the General just don\'t be rude, spam or post links in there, It is only for talking',
    'Do Not Just Randomly Talk In The Prayer Request, If You Would Like To use It For It\'s Purpose Please Feel Free To Do So, And We Will Hopefully Make Your Day Better.',
    'Pro Owner Is <@347052696613814273> So If I Am Not Around He Will Take Control And Will Look After You Until I return.',
    'Do Not Talk In Role Request Unless You Want A Role Then Just Simply Put What You Want And We Will Get You That Role.',
    'The word Fag and Faggot is banned, If you use it 3 times you will be kicked.'
]
