#!/usr/bin/python3
import os, platform, time, shutil, binascii

VERSION = "v1.1 ESP"

def prgood(content):
	print(f"[\033[0;32m✓\033[0m] {content}")

def prbad(content):
	print(f"[\033[0;91mX\033[0m] {content}")

def prinfo(content):
	print(f"[*] {content}")

def exitOnEnter(errCode = 0):
	input("[*] Pulsa Intro para salir...")
	exit(errCode)

osver = platform.system()

if osver == "Darwin":
	prbad("Error 11: macOS no esta soportado!")
	prinfo("Usa un PC con Windows o Linux.")
	exitOnEnter()

def clearScreen():
	if osver == "Windows":
		os.system("cls")
	else:
		os.system("clear")

cwd = os.path.dirname(os.path.abspath(__file__))
try:
	os.chdir(cwd)
except Exception:
	prbad("Fallo al configurar cwd: " + cwd)
	prbad("Esto no deberia de suceder casi nunca. Intenta ejecutar el script de nuevo.")
	exitOnEnter()

# Section: insureRoot
if not os.path.exists("Nintendo 3DS/"):
	prbad("Error 01: No se encontro la carpeta Nintendo 3DS! Asegurate de estar ejecutando el script desde la raiz de la SD!")
	prbad("Si no funciona, extrae la SD del PC e insertala en la 3DS/2DS. Enciendela (espera 1 min) y apagala. Saca la SD de la 3DS/2DS, insertala en el PC y ejecuta de nuevo el script.")
	prinfo(f"Carpeta actual: {cwd}")
	exitOnEnter()

# Section: sdWritable
def writeProtectCheck():
	prinfo("Comprobando si se puede escribir en la SD...")
	writeable = os.access(cwd, os.W_OK)
	try: # Bodge for windows
		with open("test.txt", "w") as f:
			f.write("test")
			f.close()
		os.remove("test.txt")
	except:
		writeable = False

	if not writeable:
		prbad("Error 02: Tu SD esta protegida contra escritura! Asegurate de que el interruptor de tu SD no este en 'Lock'.")
		prinfo("Ayuda visual: https://nintendohomebrew.com/assets/img/nhmemes/sdlock.png")
		exitOnEnter()
	else:
		prgood("Se puede escribir en la SD!")

# Section: SD card free space
# ensure 16MB free space
freeSpace = shutil.disk_usage(cwd).free
if freeSpace < 16777216:
	prbad(f"Error 06: Necesitas al menos 16MB de espacio libre en tu SD, tu tienes {(freeSpace / 1000000):.2f} bytes libres!")
	prinfo("Libera espacio en tu SD e intentalo de nuevo.")
	exitOnEnter()

clearScreen()
print(f"CONFIGURADOR de MSET9 {VERSION} por zoogie y Aven")
print(f"Traducido por Lopez Tutoriales\n")
print("Cual es el MODELO y VERSION DE SISTEMA de tu consola?")
print("La OLD 3DS/2DS tiene 2 gatillos (L and R)")
print("La NEW 3DS/2DS tiene 4 gatillos (L, R, ZL, ZR)")
print("\n-- Escriba un numero y pulse INTRO (ENTER) --\n")
print("↓ Escribe uno de estos numeros!")
print("1. OLD 3DS/2DS, desde 11.8.0 hasta 11.17.0")
print("2. NEW 3DS/2DS, desde 11.8.0 hasta 11.17.0")
print("3. OLD 3DS/2DS, desde 11.4.0 hasta 11.7.0")
print("4. NEW 3DS/2DS, desde 11.4.0 hasta 11.7.0")

encodedId1s = {
	1: "FFFFFFFA119907488546696508A10122054B984768465946C0AA171C4346034CA047B84700900A0871A0050899CE0408730064006D00630000900A0862003900",
	2: "FFFFFFFA119907488546696508A10122054B984768465946C0AA171C4346034CA047B84700900A0871A005085DCE0408730064006D00630000900A0862003900",
	3: "FFFFFFFA119907488546696508A10122054B984768465946C0AA171C4346034CA047B84700900A08499E050899CC0408730064006D00630000900A0862003900",
	4: "FFFFFFFA119907488546696508A10122054B984768465946C0AA171C4346034CA047B84700900A08459E050881CC0408730064006D00630000900A0862003900"
}
hackedId1Encoded, consoleModel, consoleFirmware = "", "", ""
while 1:
	try:
		sysModelVerSelect = input(">>> ")
		if sysModelVerSelect.startswith("11"):
			prbad("No escribas la version de sistema, solo el numero de seleccion!")
			sysModelVerSelect = 42
		sysModelVerSelect = int(sysModelVerSelect)
	except KeyboardInterrupt:
		print()
		prgood("Adios!")
		exitOnEnter()
	except:
		sysModelVerSelect = 42
	if sysModelVerSelect == 1:
		hackedId1Encoded = encodedId1s[1]
		consoleModel = "OLD3DS"
		consoleFirmware = "11.8-11.17"
		break

	if sysModelVerSelect == 2:
		hackedId1Encoded = encodedId1s[2]
		consoleModel = "NEW3DS"
		consoleFirmware = "11.8-11.17"
		break

	if sysModelVerSelect == 3:
		hackedId1Encoded = encodedId1s[3]
		consoleModel = "OLD3DS"
		consoleFirmware = "11.4-11.7"
		break

	if sysModelVerSelect == 4:
		hackedId1Encoded = encodedId1s[4]
		consoleModel = "NEW3DS"
		consoleFirmware = "11.4-11.7"
		break

	else:
		prbad("No valido, intentalo de nuevo.")

trigger = "002F003A.txt"  # all 3ds ":/" in hex
hackedId1 = bytes.fromhex(hackedId1Encoded).decode("utf-16le")  # ID1 - arm injected payload in readable format
id1 = ""
id0 = ""
realId1Path = ""

extdataRoot = ""
realId1BackupTag = "_user-id1"
id0Count = 0
id1Count = 0
id0List = []

homeMenuExtdata = [0x8F, 0x98, 0x82, 0xA1, 0xA9, 0xB1]  # us,eu,jp,ch,kr,tw
miiMakerExtdata = [0x217, 0x227, 0x207, 0x267, 0x277, 0x287]  # us,eu,jp,ch,kr,tw

# make a table so we can print regions based on what hex code from the above is found
regionTable = {
	0x8F: "Region USA",
	0x98: "Region EUR",
	0x82: "Region JPN",
	0xA1: "Region CHN",
	0xA9: "Region KOR",
	0xB1: "Region TWN"
}				

homeDataPath, miiDataPath, homeHex, miiHex = "", "", 0x0, 0x0
def sanity():
	global haxState, realId1Path, id0, id1, homeDataPath, miiDataPath, homeHex, miiHex
	menuExtdataGood = False
	miiExtdataGood = False

	print()
	prinfo("Realizando comprobaciones para evitar errores...")

	writeProtectCheck()

	prinfo("Comprobando que los archivos de la SD existen...")
	fileSanity = 0
	fileSanity += softcheck("boot9strap/boot9strap.firm", 0, 0x08129C1F, 1)
	fileSanity += softcheck("boot.firm", retval = 1)
	fileSanity += softcheck("boot.3dsx", retval = 1)
	fileSanity += softcheck("b9", retval = 1)
	fileSanity += softcheck("SafeB9S.bin", retval = 1)
	if fileSanity > 0:
		prbad("Error 08: Faltan uno o mas archivos! O estan corruptos!")
		prinfo("Copia de nuevo todos los archivos a tu SD y luego ejecuta de nuevo el script.")
		exitOnEnter()
	prgood("Todos los archivos estan correctos!")

	prinfo("Comprobando bases de datos...")
	checkTitledb = softcheck(realId1Path + "/dbs/title.db", 0x31E400, 0, 1)
	checkImportdb = softcheck(realId1Path + "/dbs/import.db", 0x31E400, 0, 1)
	if checkTitledb or checkImportdb:
		prbad("Error 10: Base(s) de datos corrupta o no esta!")
		if not (
			os.path.exists(realId1Path + "/dbs/import.db")
			or os.path.exists(realId1Path + "/dbs/title.db")
		):
			if not os.path.exists(realId1Path + "/dbs"):
				os.mkdir(realId1Path + "/dbs")
			if checkTitledb:
				open(realId1Path + "/dbs/title.db", "x").close()
			if checkImportdb:
				open(realId1Path + "/dbs/import.db", "x").close()

			prinfo("Bases de datos vacias creadas.")
		prinfo("resetea la base de datos primero en 'configuracion de la consola -> gestion de datos -> nintendo 3ds -> programas' y vuelve!")
		prinfo("Guia visual: https://3ds.hacks.guide/images/screenshots/database-reset.jpg")
		exitOnEnter()
	else:
		prgood("Las bases de datos parecen estar bien!")
	
	if os.path.exists(realId1Path + "/extdata/" + trigger):
		prinfo("Eliminando payload obsoleto...")
		os.remove(realId1Path + "/extdata/" + trigger)
	
	extdataRoot = realId1Path + "/extdata/00000000"

	prinfo("Comprobando datos adicionales del menu home...")
	for i in homeMenuExtdata:
		extdataRegionCheck = extdataRoot + f"/{i:08X}"
		if os.path.exists(extdataRegionCheck):
			prgood(f"Detectados datos {regionTable[i]} del menu home!")
			homeHex = i
			homeDataPath = extdataRegionCheck
			menuExtdataGood = True
			break
	
	if not menuExtdataGood:
		prbad("Error 04: No hay datos del menu home!")
		prinfo("Esto es raro que pase. Pon la SD en tu consola de nuevo.")
		prinfo("Enciendela y apagala, traela al PC y reinicia el script.")
		prinfo("Para ayuda, visitanos en: https://discord.gg/nintendohomebrew")
		exitOnEnter()
	
	prinfo("Comprobando datos adicionales del editor de Mii...")
	for i in miiMakerExtdata:
		extdataRegionCheck = extdataRoot + f"/{i:08X}"
		if os.path.exists(extdataRegionCheck):
			prgood("Encontrados datos del editor de Mii!")
			miiHex = i
			miiDataPath = extdataRegionCheck
			miiExtdataGood = True
			break
	
	if not miiExtdataGood:
		prbad("Error 05: No hay datos del editor de Mii!")
		prinfo("Visita https://3ds.hacks.guide/troubleshooting#installing-boot9strap-mset9 para las instrucciones.")
		exitOnEnter()

def injection():
	global realId1Path, id1

	if not os.path.exists(id0 + "/" + hackedId1):
		prinfo("Creando Id1 hackeado...")
		hackedId1Path = id0 + "/" + hackedId1
		os.mkdir(hackedId1Path)
		os.mkdir(hackedId1Path + "/extdata")
		os.mkdir(hackedId1Path + "/extdata/00000000")
	else:
		prinfo("Reutilizando Id1 hackeado existente...")
		hackedId1Path = id0 + "/" + hackedId1

	if not os.path.exists(hackedId1Path + "/dbs"):
		prinfo("Copiando bases de datos a Id1 hackeado...")
		shutil.copytree(realId1Path + "/dbs", hackedId1Path + "/dbs")

	prinfo("Copiando datos adicionales a Id1 hackeado...")
	if not os.path.exists(hackedId1Path + f"/extdata/00000000/{homeHex:08X}"):
		shutil.copytree(homeDataPath, hackedId1Path + f"/extdata/00000000/{homeHex:08X}")
	if not os.path.exists(hackedId1Path + f"/extdata/00000000/{miiHex:08X}"):
		shutil.copytree(miiDataPath, hackedId1Path + f"/extdata/00000000/{miiHex:08X}")

	prinfo("Inyectando archivo desencadenante...")
	triggerFilePath = id0 + "/" + hackedId1 + "/extdata/" + trigger
	if not os.path.exists(triggerFilePath):
		with open(triggerFilePath, "w") as f:
			f.write("plz be haxxed mister arm9, thx")
			f.close()
	
	if os.path.exists(realId1Path) and realId1BackupTag not in realId1Path:
		prinfo("Haciendo backup de Id1 real...")
		os.rename(realId1Path, realId1Path + realId1BackupTag)
		id1 += realId1BackupTag
		realId1Path = f"{id0}/{id1}"
	else:
		prinfo("Saltando backup porque ya existe un backup!")


	prgood("MSET9 inyectado con exito!")

def remove():
	global realId1Path, id0, id1
	prinfo("Eliminando MSET9...")

	if os.path.exists(realId1Path) and realId1BackupTag in realId1Path:
		prinfo("Renombrando Id1 original...")
		os.rename(realId1Path, id0 + "/" + id1[:32])
	else: 
		prgood("Nada que eliminar!")
		return
	
	# print(id1_path, id1_root+"/"+id1[:32])
	for id1Index in range(1,5): # Attempt to remove *all* hacked id1s
		maybeHackedId = bytes.fromhex(encodedId1s[id1Index]).decode("utf-16le")
		if os.path.exists(id0 + "/" + maybeHackedId):
			prinfo("Eliminando Id1 hackeado...")
			shutil.rmtree(id0 + "/" + maybeHackedId)
	id1 = id1[:32]
	realId1Path = id0 + "/" + id1
	prgood("MSET9 eliminado con exito!")

def softcheck(keyfile, expectedSize = None, crc32 = None, retval = 0):
	shortname = keyfile.rsplit("/")[-1]
	if not os.path.exists(keyfile):
		prbad(f"{shortname} no existe en la SD!")
		return retval
	elif expectedSize:
		fileSize = os.path.getsize(keyfile)
		if expectedSize != fileSize:
			prbad(f"{shortname} tiene tamano de {fileSize:,} bytes, no es el esperado de {expectedSize:,} bytes")
			return retval
	elif crc32:
		with open(keyfile, "rb") as f:
			checksum = binascii.crc32(f.read())
			if crc32 != checksum:
				prbad(f"{shortname} no fue reconocido como el archivo correcto")
				f.close()
				return retval
			f.close()
	prgood(f"{shortname} se ve bien!")
	return 0

def reapplyWorkingDir():
	try:
		os.chdir(cwd)
		return True
	except Exception:
		prbad("Error 09: Imposible reaplicar el directorio de trabajo, esta reinsertada la SD?")
		return False

# Section: sdwalk
for root, dirs, files in os.walk("Nintendo 3DS/", topdown=True):

	for name in dirs:
		# If the name doesn't contain sdmc (Ignores MSET9 exploit folder)
		if "sdmc" not in name and len(name[:32]) == 32:
			try:
				# Check to see if the file name encodes as an int (is hex only)
				hexVerify = int(name[:32], 16)
			except:
				continue
			if type(hexVerify) is int:
				# Check if the folder (which is either id1 or id0) has the extdata folder
				# if it does, it's an id1 folder
				if os.path.exists(os.path.join(root, name) + "/extdata"):
					id1Count += 1
					id1 = name
					id0 = root
					realId1Path = os.path.join(root, name)

				# Otherwise, add it to the id0 list because we need to make sure we only have one id0
				else:
					if len(name) == 32:
						id0Count += 1
						id0List.append(os.path.join(root, name))

	for name in dirs: # Run the check for existing install after figuring out the structure
		# CHeck if we have an MSET9 Hacked id1 folder
		if "sdmc" in name and len(name) == 32:
		# If the MSET9 folder doesn't match the proper haxid1 for the selected console version
			if hackedId1 != name:
				prbad("Error 03: no cambies la version de la consola en mitad del exploit MSET9!")
				prbad("Por favor reinicia la configuracion de MSET9.")
				remove()
				exitOnEnter()


prinfo("Detectado(s) ID0(s):")
for i in id0List:
	prinfo(i)
print()
if id0Count != 1:
	prbad(f"Error 07: No tienes 1 ID0 en tu carpeta Nintendo 3DS, tu tienes {id0Count} ID0!")
	prinfo("Consulta: https://3ds.hacks.guide/troubleshooting#installing-boot9strap-mset9 for help!")
	exitOnEnter()

if id1Count != 1:
	prbad(f"Error 12: No tienes 1 ID0 en tu carpeta Nintendo 3DS, tu tienes {id1Count} ID1!")
	prinfo("Consult: https://3ds.hacks.guide/troubleshooting#installing-boot9strap-mset9 for help!")
	exitOnEnter()

clearScreen()
print(f"CONFIGURADOR DE MSET9 {VERSION} por zoogie y Aven")
print("Traducido por Lopez Tutoriales")
print(f"Usando {consoleModel} {consoleFirmware}")

print("\n-- Escriba un numero y pulse INTRO (ENTER) --\n")
print("↓ Escribe uno de estos numeros!")
print("1. Hacer comprobaciones de seguridad")
print("2. Inyectar payload MSET9")
print("3. Eliminar MSET9")
print("4. Salir")

while 1:
	try:
		sysModelVerSelect = int(input(">>> "))
	except KeyboardInterrupt:
		sysModelVerSelect = 4 # exit on Ctrl+C
		print()
	except:
		sysModelVerSelect = 42

	try:
		os.chdir(cwd)
	except Exception:
		prbad("Error 09: Imposible reaplicar el directorio de trabajo, esta reinsertada la SD?")
		exitOnEnter()

	if sysModelVerSelect == 1:
		sanity()
		prgood("Todo parece estar funcional!\n")
		exitOnEnter()
	elif sysModelVerSelect == 2:
		sanity()
		injection()
		exitOnEnter()
	elif sysModelVerSelect == 3:
		remove()
		exitOnEnter()
	elif sysModelVerSelect == 4 or "exit":
		prgood("Adios!")
		break
	else:
		prinfo("No valido, intentalo de nuevo.")

time.sleep(2)