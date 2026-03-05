from typing import List, Optional, Tuple

WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

# 동점일 때 우선순위: 중앙 -> 코너 -> 변
PREFERRED_MOVES = [4,0,2,6,8,1,3,5,7]

def _check_winner(board: List[int]) -> Optional[int]:
    """보드에서 승자 판정:
       returns 1 (X 승), 2 (O 승), 0 (무승부, 빈칸 없음), None (진행중)"""
    for a,b,c in WIN_LINES:
        if board[a] != 0 and board[a] == board[b] == board[c]:
            return board[a]
    if 0 not in board:
        return 0
    return None

def _detect_multiple_winners(board: List[int]) -> bool:
    """둘 다 승리 라인이 있는 비정상 상태인지 확인"""
    winners = set()
    for a,b,c in WIN_LINES:
        if board[a] != 0 and board[a] == board[b] == board[c]:
            winners.add(board[a])
    return len(winners) > 1

def _is_valid_state(board: List[int], turn: int) -> bool:
    """보드와 turn이 일관성 있는지(가능한 배열인지) 확인.
       X가 선공이라고 가정"""
    if not isinstance(board, list) or len(board) != 9:
        return False
    if any(x not in (0,1,2) for x in board):
        return False
    if turn not in (0,1):
        return False

    x_count = board.count(1)
    o_count = board.count(2)

    # 기본 카운트 검사: X는 항상 O와 같거나 1 더 많아야 함
    if o_count > x_count or x_count - o_count > 1:
        return False

    # turn에 따른 카운트 관계:
    # - turn==0 (X 차례) 이려면 x_count == o_count
    # - turn==1 (O 차례) 이려면 x_count == o_count + 1
    if turn == 0 and x_count != o_count:
        return False
    if turn == 1 and x_count != o_count + 1:
        return False

    # 동시에 두 사람이 이긴 경우(불가능한 배열)
    if _detect_multiple_winners(board):
        return False

    # 승자가 존재하면(이미 게임 끝났으면) 불허(요구사항에 따라 -1 반환)
    if _check_winner(board) is not None:
        return False

    return True

# [수정됨] _minimax 함수: depth 인자 추가 및 점수 계산 변경
def _minimax(board: List[int], player: int, depth: int) -> Tuple[int, Optional[int]]:
    """
    minimax 재귀 (깊이 가중치 적용):
      player: 1(X) 또는 2(O)
      depth: 현재 재귀 깊이
      반환 (score, best_move)
      score: X 승 -> +10-depth, O 승 -> -10+depth, 무승부 -> 0
    """
    winner = _check_winner(board)
    if winner is not None:
        if winner == 1:
            return (10 - depth, None)  # X 승: 빨리 이길수록 점수 높음
        if winner == 2:
            return (-10 + depth, None) # O 승: 빨리 이길수록 점수 낮음 (절대값 큼)
        return (0, None) # 무승부

    moves = [m for m in PREFERRED_MOVES if board[m] == 0]
    
    # (참고) moves가 비어있는 경우는 _check_winner에서 무승부(0)로 
    # 이미 처리되었으므로 이 지점에 도달하지 않음.

    best_move = None

    if player == 1:  # X의 차례: 최대화
        best_score = -11 # 가능한 최저 점수(-10)보다 낮게 초기화
        for m in moves:
            board[m] = 1
            score, _ = _minimax(board, 2, depth + 1) # 깊이 + 1
            board[m] = 0
            
            # [수정됨] 더 명확한 최적 수 선택 로직
            # PREFERRED_MOVES 순서대로 탐색하므로, 
            # 더 좋은 점수가 나오면 교체. (점수가 같으면 먼저 나온 것 유지)
            if best_move is None or score > best_score:
                best_score = score
                best_move = m

            # [수정됨] 가지치기 (Pruning): 가장 빠른 승리(최고점)를 찾으면 중단
            # (현재 depth+1 에서 바로 이기는 경우)
            if best_score == (10 - (depth + 1)):
                break
        return best_score, best_move
    else:  # player == 2, O의 차례: 최소화
        best_score = 11 # 가능한 최고 점수(10)보다 높게 초기화
        for m in moves:
            board[m] = 2
            score, _ = _minimax(board, 1, depth + 1) # 깊이 + 1
            board[m] = 0

            # [수정됨] 더 명확한 최적 수 선택 로직
            if best_move is None or score < best_score:
                best_score = score
                best_move = m
            
            # [수정됨] 가지치기 (Pruning): 가장 빠른 승리(최저점)를 찾으면 중단
            if best_score == (-10 + (depth + 1)):
                break
        return best_score, best_move

def ai(turn: int, table: List[int]) -> int:
    """
    요청된 함수.
    - 정상: 0..8 최적 수 반환
    - 게임 종료 상태 또는 불가능한 배열: -1 반환
    """
    # 기본 유효성 + 상태 검증
    if not isinstance(table, list) or len(table) != 9:
        return -1
    if any(x not in (0,1,2) for x in table):
        return -1
    if turn not in (0,1):
        return -1

    # 가능성/종료 검사 (사용자 요구: 종결 또는 불가능하면 -1)
    if not _is_valid_state(table, turn):
        return -1

    player = 1 if turn == 0 else 2

    # [수정됨] _minimax 호출 시 depth=0 추가
    # (중요) table[:]로 복사본을 넘겨 원본 리스트(table)가 수정되지 않게 함
    score, move = _minimax(table[:], player, 0) # depth 0에서 시작

    if move is None:
        # 이 경우는 _is_valid_state에서 이미 걸러져야 하지만, 안전장치.
        return -1
    return move




# 간단 테스트 (수동 확인용)
if __name__ == "__main__":
    print("--- AI 업그레이드 테스트 ---")
    print("빈 보드, X 차례 ->", ai(0, [0]*9))  # 정상: 4 (중앙 우선)
    print("빈 보드, O 차례 ->", ai(1, [0]*9))  # 불가능한 배열 -> -1
    
    # 이미 끝난 보드 예시
    ended = [1,1,1,0,2,0,0,0,2]  # X 이미 이긴 상태
    print("이미 종료 보드 ->", ai(0, ended))    # -1
    
    # X가 1턴 만에 이길 수 있는 상황 (0번 vs 2번)
    # 0번을 두면 (0,1,2) 라인 완성
    # 2번을 둬도 (0,1,2) 라인 완성
    # PREFERRED_MOVES = [4,0,2,6,8,1,3,5,7] 이므로 '0'을 선택해야 함.
    board_win_in_1 = [1,1,0, 0,2,0, 0,2,0]
    print("X 1턴 승리 (0 vs 2) ->", ai(0, board_win_in_1)) # 0이 나와야 함

    # X가 1턴만에 이길 수 있는 수(8) vs 3턴 걸려 이기는 수(0)
    # AI는 1턴만에 이기는 '8'을 선택해야 함.
    board_fast_win = [0,2,1,
                      2,1,0,
                      0,0,0]
    # X가 8에 두면 (2,5,8)로 즉시 승리 (score: 10-1 = 9)
    # X가 0에 두면 O가 6 방어, X가 5, O가 7 방어, X가 3 (복잡하지만 8보다 늦음)
    print("빠른 승리(8) vs 느린 승리(0) ->", ai(0, board_fast_win)) # 8이 나와야 함

# (make_umm_result 함수는 AI 로직과 무관하므로 그대로 둡니다)
def make_umm_result(board, ai_turn, best):
    base = "동탄"
    umm_result = ""
    
    # 9칸 보드 처리
    for j, cell in enumerate(board):
        num_e = j + 1
        if cell == 0:      # 빈칸
            suffix = ""
        elif cell == 1:    # X
            suffix = ","
        elif cell == 2:    # O
            suffix = ",,"
        else:
            suffix = ""
        umm_result += base + '어'*num_e + suffix + "?"
    
    # AI 선택 칸 처리
    umm_result += '어'*best + '엄' + '어'*best
    if ai_turn == 0:      # X
        umm_result += '어.'
    else:                 # O
        umm_result += '어..'
    
    return umm_result








def make_umm_result(board, ai_turn, best):
    base = "동탄"
    umm_result = ""
    
    # 9칸 보드 처리
    for j, cell in enumerate(board):
        num_e = j + 1
        if cell == 0:      # 빈칸
            suffix = ""
        elif cell == 1:    # X
            suffix = ","
        elif cell == 2:    # O
            suffix = ",,"
        else:
            suffix = ""
        umm_result += base + '어'*num_e + suffix + "?"
    
    # AI 선택 칸 처리
    umm_result += '어'*best + '엄' + '어'*best
    if ai_turn == 0:      # X
        umm_result += '어.'
    else:                 # O
        umm_result += '어..'
    
    return umm_result

# 예시 Board와 AI Move
# board = [2, 2, 1, 2, 2, 1, 1, 1, 0]  # 0:빈, 1:X, 2:O
# ai_turn = 0  # 0:X, 1:O
# best = 8     # AI Move (0~8)

# result = make_umm_result(board, ai_turn, best)
# print(result)



import itertools

# 0,1,2 중 하나를 9자리 배열로 조합
options = [0, 1, 2]
all_combinations = itertools.product(options, repeat=9)


total_count = 0        # 전체 조합 번호
valid_count = 0        # -1 아닌 경우 번호

results = []  # 결과를 임시로 저장할 리스트

for combo in all_combinations:
    total_count += 1
    combo_list = list(combo)
    
    for player in [0, 1]:
        move = ai(player, combo_list)
        if move != -1:
            valid_count += 1
            print(f"전체 {total_count}번째, -1 아님 {valid_count}번째")
            print("Player:", player)
            print("Board:", combo_list)
            print("AI Move:", move)
            
            result = make_umm_result(combo_list, player, move)
            print(result)
            results.append(result)  # 파일 대신 리스트에 저장
            
            print('-----------------------')

# --- 모든 결과를 역순으로 저장 ---
with open("case.umm", "w", encoding="utf-8") as f:
    for result in reversed(results):  # 역순으로 파일에 기록
        f.write(result + "\n")