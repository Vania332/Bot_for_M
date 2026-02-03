import random

def play_coin(bet: int) -> tuple[bool, int]:
    """
    Чистая логика орёл/решка.
    Возвращает: (победа, выплата)
    
    Примеры:
        play_coin(50) → (True, 100)   # Выигрыш: 50 × 2 = 100
        play_coin(50) → (False, 0)    # Проигрыш
    """
    win = random.random() > 0.51
    payout = bet * 2 if win else 0
    return win, payout