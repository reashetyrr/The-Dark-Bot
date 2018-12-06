from colorama import Fore, init

init()

print(f'{Fore.GREEN}Welcome to the cog generator')
print('Please enter the cogs location (THIS HAS TO BE THE ABSOLUTE PATH)')
cog_path = input(f'{Fore.RESET}Path:')
print(f'{Fore.GREEN}Please enter the cog name', f'{Fore.RED} WITHOUT the cog prefix')
cog_name = input(f'{Fore.RESET}Cog name:')

cog_file = cog_name.lower() + '.py'
print(f'Your file will be: {cog_path}\\{cog_file}')
