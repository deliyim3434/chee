

from pyrogram import Client
from che import config, logger


class Userbot(Client):
    def __init__(self):
        """
        Userbot'u birden fazla istemci (client) ile başlatır.

        Bu yöntem, önceden tanımlanmış oturum dizelerini (session strings) kullanarak 
        userbot için istemcileri kurar. Her istemciye, 'clients' sözlüğündeki anahtara 
        dayalı benzersiz bir ad atanır.
        """
        self.clients = []
        clients = {"one": "SESSION1", "two": "SESSION2", "three": "SESSION3"}
        for key, string_key in clients.items():
            name = f"cheUB{key[-1]}"
            session = getattr(config, string_key)
            setattr(
                self,
                key,
                Client(
                    name=name,
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=session,
                ),
            )

    async def boot_client(self, num: int, ub: Client):
        """
        Bir istemciyi başlatır ve ilk kurulumu gerçekleştirir.
        
        Argümanlar:
            num (int): Başlatılacak istemci numarası (1, 2 veya 3).
            ub (Client): Userbot istemci örneği.
            
        Hatalar:
            SystemExit: İstemci, log grubuna mesaj gönderemezse işlemi durdurur.
        """
        clients = {
            1: self.one,
            2: self.two,
            3: self.three,
        }
        client = clients[num]
        await client.start()
        try:
            await client.send_message(config.LOGGER_ID, "Asistan Başlatıldı")
        except:
            raise SystemExit(f"Asistan {num}, log grubuna mesaj gönderemediği için durduruldu.")

        client.id = ub.me.id
        client.name = ub.me.first_name
        client.username = ub.me.username
        client.mention = ub.me.mention
        self.clients.append(client)
        try:
            await ub.join_chat("FallenAssociation")
        except:
            pass
        logger.info(f"Asistan {num}, @{client.username} olarak başlatıldı.")

    async def boot(self):
        """
        Asistanları asenkron olarak başlatır.
        """
        if config.SESSION1:
            await self.boot_client(1, self.one)
        if config.SESSION2:
            await self.boot_client(2, self.two)
        if config.SESSION3:
            await self.boot_client(3, self.three)

    async def exit(self):
        """
        Asistanları asenkron olarak durdurur.
        """
        if config.SESSION1:
            await self.one.stop()
        if config.SESSION2:
            await self.two.stop()
        if config.SESSION3:
            await self.three.stop()
        logger.info("Asistanlar durduruldu.")
