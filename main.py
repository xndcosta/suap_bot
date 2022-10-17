from tkinter.ttk import Separator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import discord

USERNAME = ''
PASSWORD = ''
DISCORD_TOKEN = ''

def remove_unicode( str ):
    encoded_string = str.encode( 'ascii', 'ignore' )
    return encoded_string.decode( )

client = discord.Client( intents= discord.Intents.default( ) )

@client.event
async def on_ready( ):
    # Headlles
    chrome_options = Options()
    chrome_options.add_argument( '--headless' )
    chrome_options.add_argument( '--window-size=1920,1080' )

    #  Login
    driver = webdriver.Chrome( chrome_options= chrome_options )
    driver.get( 'https://suap.ifsuldeminas.edu.br/accounts/login/' )

    box = driver.find_element( By.NAME, 'username' )
    box.send_keys( USERNAME )

    box = driver.find_element( By.NAME, 'password' )
    box.send_keys( PASSWORD )

    box = driver.find_element( By.XPATH, "//input[@type='submit']" )
    box.click( )


    # Scrap boletim
    driver.get( 'https://suap.ifsuldeminas.edu.br/djtools/breadcrumbs_reset/ensino_boletins/edu/boletim_aluno/' )

    detalhes_materia = driver.find_elements( By.LINK_TEXT, 'Detalhar' )
    links_materias = [ _.get_attribute( 'href' ) for _ in detalhes_materia ]
    notas = []

    for link in links_materias:
        driver.get( link )
        
        box = driver.find_element( By.TAG_NAME, 'h2' )
        notas_materia = []
        notas_materia.append( remove_unicode( box.get_attribute( 'innerHTML' )[ 7: ] ) )
        
        box = driver.find_element( By.TAG_NAME, 'tbody' )
        notas_box = box.find_elements( By.TAG_NAME, 'tr' )
        
        for nota in notas_box:
            temp_box = nota.find_elements( By.TAG_NAME, 'td' )
            nota = temp_box[ len( temp_box ) - 1 ].get_attribute( 'innerHTML' )
            notas_materia.append( nota )
            
        notas.append( notas_materia )
            
    driver.close( )

    # Verificação das notas
    linhas = []
    materias = []
    novo = True

    with open( 'notas.txt', 'r', encoding = 'utf8' ) as arq:
        linhas = arq.readlines( )
        
        for i in range( len( linhas ) ):
            linhas[ i ] = linhas[ i ].split( ';' )
            
            if len( linhas[ i ] ) - 1 != len( notas[ i ] ):
                materias.append( linhas[i][0] )
                novo = True
            else:
                for j in range( len( linhas[ i ] ) - 1 ):
                    if remove_unicode( linhas[ i ][ j ] ) != remove_unicode( notas[ i ][ j ] ):
                        materias.append( notas[ i ][ 0 ] )
                        novo = True
                        break
        
    if novo:
        for server in client.guilds:
            channel = discord.utils.get( server.channels, name = "notas" )
            
        title = 'Nota nova'
        embed = discord.Embed( title = title, description = [ f'{_}\n' for _ in materias ], color = discord.Color.blue( ), url = 'https://suap.ifsuldeminas.edu.br/accounts/login' )
        await channel.send( embed = embed )
        
        with open( 'notas.txt', 'w', encoding = 'utf8' ) as arq:
            for linha in notas:
                for nota in linha:
                    arq.write( f'{nota};' )
                arq.write( '\n' )
                
client.run( DISCORD_TOKEN )
        