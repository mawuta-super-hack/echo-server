import asyncio
import logging
import random
import string
import sys
from asyncio.streams import StreamReader, StreamWriter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Server:

    def __init__(self, host: str = '127.0.0.1', port: int = 8000):
        self.host = host
        self.port = port

    async def client_connected(
            self,
            reader: StreamReader,
            writer: StreamWriter
    ):
        address = writer.get_extra_info('peername')
        logger.info('[Server] Start serving %s', address)

        while True:
            data = await reader.read(1024)
            if not data:
                break
            writer.write(data)
            await writer.drain()

        logger.info('[Server] Stop serving %s', address)
        writer.close()

    async def start(self, host: str, port: int):
        return await asyncio.start_server(
            self.client_connected, host, port)


class Client:

    def __init__(self, host: str = '127.0.0.1', port: int = 8000, id: int = 1):
        self.host = host
        self.port = port
        self.client_id = id

    async def start(self):
        reader, writer = await asyncio.open_connection(
            self.host,
            self.port
        )

        for _ in range(5):
            message = self.random_string(self.client_id)
            await self.delay()

            writer.write(message.encode())
            await writer.drain()

            if message := await reader.read(1024):
                logger.info(message.decode())

        logger.info('[Client %s] Close the connection', self.client_id)
        writer.close()
        await writer.wait_closed()

    def random_string(self, id: int):
        letters = string.ascii_lowercase
        message_strs = ''.join(random.choice(letters) for _ in range(8))
        return f'[Client {id}] {message_strs}'

    async def delay(self):
        rand_delay = random.randint(5, 10)
        await asyncio.sleep(rand_delay)


async def main():
    running_server = await asyncio.create_task(
        Server().start('127.0.0.1', 8000)
    )

    all_clients = []
    for i in range(1, 11):
        client = Client(host='127.0.0.1', port=8000, id=i)
        task = asyncio.create_task(client.start())
        all_clients.append(task)

    await asyncio.gather(*all_clients, return_exceptions=True)
    running_server.close()


if __name__ == '__main__':
    asyncio.run(main())
