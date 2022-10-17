from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import discord
import pickle

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
    print( '[!] Logando')
    driver = webdriver.Chrome( service= Service( ChromeDriverManager( ).install( ) ), options= chrome_options )
    driver.get( 'https://suap.ifsuldeminas.edu.br/accounts/login/' )

    box = driver.find_element( By.NAME, 'username' )
    box.send_keys( USERNAME )

    box = driver.find_element( By.NAME, 'password' )
    box.send_keys( PASSWORD )

    box = driver.find_element( By.XPATH, "//input[@type='submit']" )
    box.click( )


    # Scrap boletim
    print( '[!] Scraping')
    driver.get( 'https://suap.ifsuldeminas.edu.br/djtools/breadcrumbs_reset/ensino_boletins/edu/boletim_aluno/' )
    
    materias = dict( )
    links_materias = [ _.get_attribute( 'href' ) for _ in driver.find_elements( By.LINK_TEXT, 'Detalhar' ) ]
    for link in links_materias:
        driver.get( link )
        
        nome_materia = remove_unicode( driver.find_element( By.TAG_NAME, 'h2' ).get_attribute( 'innerHTML' )[ 7: ] )
        materias[ nome_materia ] = list( )
        
        tabela = driver.find_element( By.TAG_NAME, 'tbody' )
        linhas = tabela.find_elements( By.TAG_NAME, 'tr' )
        for l in linhas:
            col = l.find_elements( By.TAG_NAME, 'td' )
            
            atividade = col[ 0 ].get_attribute( 'innerHTML' )
            nota = col[ 5 ].get_attribute( 'innerHTML' )
            
            materias[nome_materia].append( [ atividade, nota ] )
            
    driver.close( )

    # Verificação das notas
    print( '[!] Verificando')

    with open( 'D:/Users/alexa/Desktop/Programacao/suap-if-passos/notas.pkl', 'rb' ) as arq:
        materias_arq = pickle.load( arq )
        novo = { k: materias[ k ] for k in materias if k in materias_arq and materias[ k ] != materias_arq[ k ] }
           
    if novo:
        print( '[!] Notas novas' )
        
        for server in client.guilds:
            channel = discord.utils.get( server.channels, name= "📓suap" )
            
            title = 'Nota nova'
            text = ''
            for materia in materias:
                text += f'{materia}\n'
                for atv in materias[materia]:
                    text += f'\t- {atv[ 0 ]}\n'
                
            embed = discord.Embed( title= title, description= text, color= discord.Color.blue( ), url= 'https://suap.ifsuldeminas.edu.br/accounts/login' )

            await channel.send( embed= embed )
        
        print( '[!] Reescrevendo notas' )
        
        with open( 'D:/Users/alexa/Desktop/Programacao/suap-if-passos/notas.pkl', 'wb') as arq:
            pickle.dump( novo, arq, protocol= -1 )

    await client.close()
                
client.run( DISCORD_TOKEN, log_handler = None )
        