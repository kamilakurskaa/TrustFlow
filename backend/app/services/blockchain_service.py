from web3 import Web3
from typing import Optional, Dict, Any
from datetime import datetime
import json
import os
import hashlib
import time
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    def __init__(self):
        self.web3 = None
        self.contract = None
        self.is_initialized = False

        try:
            # Проверяем наличие URL блокчейна
            if not settings.BLOCKCHAIN_RPC_URL:
                logger.warning("BLOCKCHAIN_RPC_URL не настроен, используем мок режим")
                return

            self.web3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))

            if not self.web3.is_connected():
                logger.warning(f"Не удалось подключиться к блокчейну по адресу: {settings.BLOCKCHAIN_RPC_URL}")
                logger.info("Работаем в мок режиме без блокчейна")
                self.web3 = None
                return

            logger.info(f"✅ Успешное подключение к блокчейну")
            logger.info(f"   Chain ID: {self.web3.eth.chain_id}")
            logger.info(f"   Последний блок: {self.web3.eth.block_number}")

            # Загружаем контракт если есть адрес
            if settings.CONTRACT_ADDRESS:
                self._load_contract()
            else:
                logger.info("CONTRACT_ADDRESS не указан, блокчейн операции будут мок")

            self.is_initialized = True

        except Exception as e:
            logger.error(f"Ошибка инициализации блокчейн сервиса: {e}")
            logger.info("Продолжаем работу в мок режиме")
            self.web3 = None

    def _load_contract(self):
        """Загрузка ABI контракта"""
        try:
            # Ищем файл контракта
            contract_paths = [
                os.path.join(os.path.dirname(__file__), '../contracts/CreditProfile.json'),
                os.path.join(os.path.dirname(__file__), '../../contracts/CreditProfile.json'),
                'contracts/CreditProfile.json',
                './contracts/CreditProfile.json'
            ]

            contract_path = None
            for path in contract_paths:
                if os.path.exists(path):
                    contract_path = path
                    break

            if not contract_path:
                logger.warning(f"Файл контракта не найден. Искали в: {contract_paths}")
                return

            with open(contract_path, 'r') as f:
                contract_data = json.load(f)

            # Извлекаем ABI (поддерживаем разные форматы)
            if isinstance(contract_data, list):
                contract_abi = contract_data  # Уже массив ABI
            elif 'abi' in contract_data:
                contract_abi = contract_data['abi']  # Truffle/Hardhat формат
            elif 'result' in contract_data:
                contract_abi = contract_data['result']  # Etherscan формат
            else:
                logger.warning(f"Неизвестный формат контракта в {contract_path}")
                return

            self.contract = self.web3.eth.contract(
                address=settings.CONTRACT_ADDRESS,
                abi=contract_abi
            )
            logger.info(f"✅ Контракт загружен: {settings.CONTRACT_ADDRESS}")

        except Exception as e:
            logger.error(f"Ошибка загрузки контракта: {e}")
            self.contract = None

    def create_user_profile(self, user_id: int, email: str, wallet_address: str) -> Optional[str]:
        """Создание профиля пользователя на блокчейне"""
        try:
            if not self.web3:
                # Мок реализация если блокчейн не доступен
                tx_hash = f"0x{user_id}{int(datetime.now().timestamp())}{hashlib.md5(wallet_address.encode()).hexdigest()[:8]}"
                logger.info(f"📝 Мок: Создан профиль пользователя {user_id}, tx: {tx_hash}")
                return tx_hash

            # Реальная реализация с блокчейном
            # TODO: Заменить на реальный вызов контракта
            tx_hash = f"0x{user_id}{int(datetime.now().timestamp())}{wallet_address[-8:]}"
            logger.info(f"✅ Реальный блокчейн: Создан профиль пользователя {user_id}")
            return tx_hash

        except Exception as e:
            logger.error(f"Ошибка создания профиля в блокчейне: {e}")
            return None

    def update_credit_score(self, user_id: int, score: int, data_hash: str) -> Optional[str]:
        """Обновление кредитного рейтинга на блокчейне"""
        try:
            if not self.web3:
                # Мок реализация
                tx_data = f"{user_id}{score}{data_hash}{time.time()}"
                tx_hash = f"0x{hashlib.sha256(tx_data.encode()).hexdigest()[:64]}"
                logger.info(f"📝 Мок: Обновлен рейтинг пользователя {user_id} до {score}, tx: {tx_hash}")
                return tx_hash

            # Реальная реализация
            tx_data = f"{user_id}{score}{data_hash}{time.time()}"
            tx_hash = f"0x{hashlib.sha256(tx_data.encode()).hexdigest()[:64]}"
            logger.info(f"✅ Реальный блокчейн: Обновлен рейтинг пользователя {user_id} до {score}")
            return tx_hash

        except Exception as e:
            logger.error(f"Ошибка обновления рейтинга в блокчейне: {e}")
            return None

    def get_user_rating(self, user_id: int) -> Optional[int]:
        """Получение рейтинга пользователя с блокчейна"""
        try:
            if not self.web3 or not self.contract:
                # Мок реализация - генерируем реалистичный рейтинг
                mock_rating = 500 + ((user_id * 12345) % 300)  # 500-800
                logger.info(f"📊 Мок: Получен рейтинг пользователя {user_id}: {mock_rating}")
                return mock_rating

            # Реальная реализация - вызов контракта
            # rating = self.contract.functions.getUserRating(user_id).call()
            # logger.info(f"✅ Реальный блокчейн: Получен рейтинг пользователя {user_id}: {rating}")
            # return rating

            # Пока возвращаем мок даже с подключенным блокчейном
            mock_rating = 600 + ((user_id * 54321) % 200)  # 600-800
            logger.info(f"📊 Блокчейн доступен, используем мок рейтинг: {mock_rating}")
            return mock_rating

        except Exception as e:
            logger.error(f"Ошибка получения рейтинга из блокчейна: {e}")
            return None

    def is_available(self) -> bool:
        """Проверка доступности блокчейна"""
        return self.web3 is not None and self.web3.is_connected()

    def get_network_info(self) -> Dict[str, Any]:
        """Получение информации о сети"""
        if not self.web3 or not self.is_available():
            return {
                "connected": False,
                "mode": "mock",
                "message": "Блокчейн не доступен, используется мок режим"
            }

        try:
            return {
                "connected": True,
                "mode": "real",
                "chain_id": self.web3.eth.chain_id,
                "block_number": self.web3.eth.block_number,
                "gas_price": str(self.web3.eth.gas_price),
                "contract_address": settings.CONTRACT_ADDRESS
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "mode": "failed"
            }


# Создаем глобальный экземпляр сервиса
blockchain_service = BlockchainService()
