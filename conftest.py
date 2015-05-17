# -*- coding: utf-8 -*-
import pytest
import logging

@pytest.fixture(scope='session', autouse=True)
def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('test_flow.log')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("\n\n     ##########   NEW TEST SESSION STARTED   ########## \n")

@pytest.fixture(scope='function', autouse=True)
def log_test_case(request):
    logging.info('Test "%s" started', request.module.__name__ + "." + request.function.__name__)
    def log_finish():
        logging.info('Test "%s" finished \n', request.module.__name__ + "." + request.function.__name__)
    request.addfinalizer(log_finish)

