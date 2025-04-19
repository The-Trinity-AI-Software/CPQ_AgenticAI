# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 17:31:56 2025

@author: HP
"""

import logging
import os
from datetime import datetime

def setup_logger():
    log_dir = r"G:/MVP/mnt/data/CPQ_Agentic_Workflow/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = f"cpq_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        filemode="w"  # overwrite each time; use "a" to append
    )

    return logging.getLogger("cpq_logger")
