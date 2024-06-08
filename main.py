from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, sys, os
import validacpfcnpj

def clickByXpath(xpath):
	# AGUARDA CLICK BOTAO CARREGAR E CLICA NO MESMO
	wait = WebDriverWait(driver, 10)
	button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
	button.click()

	try:
		input_field = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
	except:
		input_field = None

	return input_field


def CheckPIXkey(chaves_pix):
	def typeKey(pix_data):
		clickByXpath('//*[@id="tipo-chave-pix"]')

		cpf_cnpj = validacpfcnpj.ValidaCpfCnpj(pix_data)

		if cpf_cnpj.valida():
			pix_data = pix_data.replace(".", "").replace("-", "").replace("/", "")
			clickByXpath('/html/body/div[2]/div/div[3]/form/ul/li[6]/div/div/div[1]/div/div[2]/div[3]/div[1]/select/option[3]')
			input = clickByXpath('//*[@id="3"]')

		elif "@" in pix_data and "." in pix_data:
			clickByXpath('/html/body/div[2]/div/div[3]/form/ul/li[6]/div/div/div[1]/div/div[2]/div[3]/div[1]/select/option[2]')
			input = clickByXpath('//*[@id="2"]')

		elif len(pix_data) == 11:
			clickByXpath('/html/body/div[2]/div/div[3]/form/ul/li[6]/div/div/div[1]/div/div[2]/div[3]/div[1]/select/option[1]')
			input = clickByXpath('//*[@id="1"]')
		else:
			clickByXpath('/html/body/div[2]/div/div[3]/form/ul/li[6]/div/div/div[1]/div/div[2]/div[3]/div[1]/select/option[4]')
			input = clickByXpath('//*[@id="5"]')

		input.send_keys(pix_data)
		clickByXpath('//*[@id="valorTransferencia"]')
		time.sleep(3)

		try:
			WebDriverWait(driver, 3).until(
				EC.visibility_of_element_located((By.CLASS_NAME, "pgr-dados-cliente"))
			)

			instituicao = driver.find_element(By.ID, "instituicaoRecebedorPix").text
			nome = driver.find_element(By.ID, "nomeCliente").text
			cpf_cnpj = driver.find_element(By.ID, "cpfCnpjCliente").text

			if len(nome) > 2 and len(instituicao) > 2 and len(cpf_cnpj) > 2:
				print(f"+ Chave PIX {pix_data} - {instituicao} - {nome} - {cpf_cnpj}")
		except:
			None

	print ("[!] Acessando pagina PIX")
	time.sleep(3)
	# CLICA NO BOTÃO PESQUISA E BUSCA POR PIX
	input = clickByXpath('//*[@id="acheFacil"]')
	input.send_keys("Pix")
	time.sleep(2)

	# CLICA NO BOTÃO PAGAR COM PIX
	WebDriverWait(driver, 10).until(
		EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Pix - Pagar com Pix - Pagar ou transferir com Pix"))
	).click()

	print (f"[!] Iniciando verificação de {len(chaves_pix)} chave(s)")
	for i in chaves_pix:
		typeKey(i)


def main():

	chave_pix = sys.argv[1]
	if os.path.isfile(chave_pix):
		with open(chave_pix) as f:
			chave_pix = f.read().split("\n")
			chave_pix.remove("")
	else:
		chave_pix = [chave_pix]

	print (f"[!] {len(chave_pix)} chave(s) a verificar.")

	global driver
	options = Options()
	options.headless = False  # Altere para True se não quiser abrir a janela do navegador
	driver = webdriver.Firefox(options=options)

	agencia = "" # ADICIONAR CREDENCIAIS PARA LOGIN NO BANCO
	conta = ""
	senha = ""

	try:
		print (f"[!] Iniciando login no BB")
		# FAZ LOGIN NO BB
		driver.get("https://www2.bancobrasil.com.br/aapf/login.html")

		print (f"[!] Entrando com dados de agencia e conta")
		# CLICA NO BOTAO AGENCIA
		time.sleep(2)
		input_field = clickByXpath('//*[@id="dependenciaOrigem"]')
		input_field.send_keys(agencia)
		time.sleep(1)

		# CLICA NO BOTAO CONTA
		input_field = clickByXpath('//*[@id="numeroContratoOrigem"]')
		input_field.send_keys(conta)

		time.sleep(1)
		# CLICA NO BOTAO ENVIAR
		clickByXpath('//*[@id="botaoEnviar"]')

		time.sleep(2)
		print ("[!] Entrando com senha bancaria")
		# CLICA NO BOTAO SENHA
		input_field = clickByXpath('//*[@id="senhaConta"]')
		input_field.send_keys(senha)

		time.sleep(1)
		# CLICA NO BOTAO ENTRAR
		clickByXpath('//*[@id="botaoEnviar"]')

		print ("[!] Autenticação feita com Sucesso")
		CheckPIXkey(chave_pix)
		# Aguarda alguns segundos antes de fechar, ou mais ações podem ser adicionadas aqui
		input("Pressione Enter para fechar o navegador...")

	finally:
		driver.quit()

if __name__ == "__main__":
	main()
