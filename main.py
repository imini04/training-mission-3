import json
import os
import time

EPSILON = 1e-9
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.json")


# ==========================================
# 1. 핵심 연산 및 유틸리티
# ==========================================
def mac_2d(matrix_a, matrix_b):
    """2차원 배열 기반 MAC 연산 (O(N^2))"""
    n = len(matrix_a)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += matrix_a[i][j] * matrix_b[i][j]
    return total


def mac_1d(flat_a, flat_b):
    """[보너스 1] 1차원 평탄화 배열 기반 MAC 연산"""
    total = 0.0
    for idx in range(len(flat_a)):
        total += flat_a[idx] * flat_b[idx]
    return total


def flatten_matrix(matrix):
    """2차원 리스트를 1차원 리스트로 변환"""
    return [val for row in matrix for val in row]


def normalize_label(raw_label):
    """라벨 표준화: '+', 'cross' -> 'Cross' / 'x', 'X' -> 'X'"""
    if not isinstance(raw_label, str):
        return "UNKNOWN"
    cleaned = raw_label.strip().lower()
    if cleaned in ("+", "cross"):
        return "Cross"
    if cleaned == "x":
        return "X"
    return raw_label


def fmt_score(value):
    """점수를 보기 좋게 출력 (정수값도 1.0 형태로)"""
    text = f"{value:.16g}"
    if "." not in text and "e" not in text and "n" not in text:
        text += ".0"
    return text


def judge_scores(score_a, score_b, label_a="A", label_b="B"):
    """epsilon 기반 점수 판정"""
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    return label_a if score_a > score_b else label_b


def validate_square_matrix(matrix, expected_n):
    """N x N 정방행렬 유효성 및 숫자 타입 검증"""
    if not isinstance(matrix, list) or len(matrix) != expected_n:
        return False, f"행 개수 불일치 (기대: {expected_n}, 실제: {len(matrix) if isinstance(matrix, list) else 'N/A'})"
    for r_idx, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != expected_n:
            return False, f"{r_idx + 1}행 열 개수 불일치 (기대: {expected_n})"
        for val in row:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return False, "숫자가 아닌 데이터 포함"
    return True, "OK"


def measure_mac_performance(matrix_a, matrix_b, iterations=10):
    """I/O를 제외한 순수 MAC 연산 평균 시간(ms) 측정"""
    start = time.perf_counter()
    for _ in range(iterations):
        mac_2d(matrix_a, matrix_b)
    end = time.perf_counter()
    avg_ms = ((end - start) / iterations) * 1000.0
    return avg_ms


# ==========================================
# [보너스 2] 패턴 생성기
# ==========================================
def generate_patterns(n):
    """N x N 크기의 Cross 및 X 패턴 자동 생성"""
    mid = n // 2
    cross = [[0.0] * n for _ in range(n)]
    x_pat = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == mid or j == mid:
                cross[i][j] = 1.0
            if i == j or i + j == n - 1:
                x_pat[i][j] = 1.0
    return cross, x_pat


# ==========================================
# 2. 모드 1: 사용자 입력 (3x3)
# ==========================================
def input_3x3_matrix(name):
    print(f"{name} (3줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < 3:
        line = input(f"  {len(matrix) + 1}행: ").strip()
        parts = line.split()
        if len(parts) != 3:
            print("  [오류] 입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
            continue
        try:
            row = [float(x) for x in parts]
            matrix.append(row)
        except ValueError:
            print("  [오류] 숫자 파싱 실패: 유효한 숫자만 입력하세요.")
    return matrix


def run_mode_1():
    print("\n#---------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")
    filter_a = input_3x3_matrix("필터 A")
    print()
    filter_b = input_3x3_matrix("필터 B")

    print("\n✓ 필터 A, B 저장 완료")
    for name, mat in (("A", filter_a), ("B", filter_b)):
        print(f"  필터 {name}: " + " / ".join(" ".join(f"{v:g}" for v in row) for row in mat))

    print("\n#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")
    pattern = input_3x3_matrix("패턴")

    score_a = mac_2d(pattern, filter_a)
    score_b = mac_2d(pattern, filter_b)
    avg_time_ms = measure_mac_performance(pattern, filter_a, iterations=10)
    verdict = judge_scores(score_a, score_b, "A", "B")

    print("\n#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    print(f"A 점수: {fmt_score(score_a)}")
    print(f"B 점수: {fmt_score(score_b)}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.4f} ms")
    if verdict == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {verdict}")
    print("\n#---------------------------------------")
    print("# [4] 성능 분석 (평균/10회)")
    print("#---------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<16} {'연산 횟수(N²)':<12}")
    print("-" * 42)
    print(f"{'3x3':<10} {avg_time_ms:<16.4f} {9:<12}")


# ==========================================
# 3. 모드 2: data.json 분석
# ==========================================
def run_mode_2(filepath="data.json"):
    if not os.path.exists(filepath):
        print(f"\n[오류] '{filepath}' 파일을 찾을 수 없습니다. 같은 폴더에 위치시켜 주세요.")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"\n[오류] JSON 파싱 실패: {e}")
        return

    if not isinstance(data, dict):
        print("\n[오류] data.json 최상위 구조가 객체({})가 아닙니다.")
        return

    raw_filters = data.get("filters", {})
    raw_patterns = data.get("patterns", {})
    if not isinstance(raw_filters, dict):
        print("\n[경고] filters 형식 오류: 객체({})가 아니므로 빈 값으로 처리합니다.")
        raw_filters = {}
    if not isinstance(raw_patterns, dict):
        print("\n[경고] patterns 형식 오류: 객체({})가 아니므로 빈 값으로 처리합니다.")
        raw_patterns = {}

    
    # [1] 필터 로드 및 라벨 정규화
    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")
    normalized_filters = {}
    for size_key, f_dict in raw_filters.items():
        try:
            n = int(size_key.split("_")[1])
        except (IndexError, ValueError):
            print(f"✗ {size_key}: 잘못된 필터 키 형식")
            continue

        if not isinstance(f_dict, dict):
            print(f"✗ {size_key}: 필터 형식 오류 (cross/x 객체가 아님)")
            continue

        normalized_filters[n] = {}
        for f_label, matrix in f_dict.items():
            std_label = normalize_label(f_label)
            valid, msg = validate_square_matrix(matrix, n)
            if valid:
                normalized_filters[n][std_label] = matrix
            else:
                print(f"✗ {size_key} ({std_label}) 검증 실패: {msg}")

        loaded_keys = ", ".join(normalized_filters[n].keys())
        if len(normalized_filters[n]) == 2:
            print(f"✓ {size_key:<7} 필터 로드 완료 ({loaded_keys})")
        else:
            print(f"✗ {size_key:<7} 필터 로드 불완전 ({loaded_keys or '없음'})")

    # [2] 패턴 분석
    print("\n#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")
    total_tests = 0
    passed_tests = 0
    failed_cases = []
    perf_samples = {}  # 크기별 성능 측정을 위한 샘플 저장

    for pat_key, pat_obj in raw_patterns.items():
        total_tests += 1
        print(f"-- {pat_key} ---")

        # 키에서 크기 N 추출 (예: size_5_1 -> 5)
        try:
            parts = pat_key.split("_")
            n = int(parts[1])
        except (IndexError, ValueError):
            reason = "패턴 키에서 크기(N) 추출 실패"
            print(f"결과: FAIL ({reason})\n")
            failed_cases.append((pat_key, reason))
            continue

        # 해당 크기의 Cross, X 필터 존재 여부 확인
        if n not in normalized_filters or "Cross" not in normalized_filters[n] or "X" not in normalized_filters[n]:
            reason = f"size_{n}에 해당하는 Cross/X 필터 누락"
            print(f"결과: FAIL ({reason})\n")
            failed_cases.append((pat_key, reason))
            continue
        
        if not isinstance(pat_obj, dict):
            reason = "패턴 항목 형식 오류 (input/expected 객체가 아님)"
            print(f"결과: FAIL ({reason})\n")
            failed_cases.append((pat_key, reason))
            continue
        
        input_matrix = pat_obj.get("input")
        expected_raw = pat_obj.get("expected")
        expected_std = normalize_label(expected_raw)

        # 입력 행렬 크기 검증
        valid, msg = validate_square_matrix(input_matrix, n)
        if not valid:
            reason = f"크기/데이터 불일치 - {msg}"
            print(f"결과: FAIL ({reason})\n")
            failed_cases.append((pat_key, reason))
            continue

        cross_filter = normalized_filters[n]["Cross"]
        x_filter = normalized_filters[n]["X"]

        if n not in perf_samples:
            perf_samples[n] = (input_matrix, cross_filter)

        score_cross = mac_2d(input_matrix, cross_filter)
        score_x = mac_2d(input_matrix, x_filter)
        verdict = judge_scores(score_cross, score_x, "Cross", "X")

        print(f"Cross 점수: {fmt_score(score_cross)}")
        print(f"X 점수: {fmt_score(score_x)}")

        if verdict == expected_std:
            passed_tests += 1
            print(f"판정: {verdict} | expected: {expected_std} | PASS\n")
        else:
            if expected_std not in ("Cross", "X"):
                reason = f"알 수 없는 expected 라벨 '{expected_raw}'"
            elif verdict == "UNDECIDED":
                reason = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"
            else:
                reason = f"판정 불일치 (판정: {verdict}, 기대: {expected_std})"
            failed_cases.append((pat_key, reason))
            print(f"판정: {verdict} | expected: {expected_std} | FAIL ({reason})\n")

    # [3] 성능 분석 (3x3 기본 포함 + 로드된 크기)
    print("#---------------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#---------------------------------------")
    if 3 not in perf_samples:
        c3, x3 = generate_patterns(3)
        perf_samples[3] = (c3, x3)

    print(f"{'크기':<10} {'평균 시간(ms)':<16} {'연산 횟수(N²)':<12}")
    print("-" * 42)
    for n in sorted(perf_samples.keys()):
        mat_a, mat_b = perf_samples[n]
        avg_ms = measure_mac_performance(mat_a, mat_b, iterations=10)
        ops = n * n
        size_str = f"{n}x{n}"
        print(f"{size_str:<10} {avg_ms:<16.4f} {ops:<12}")

    # [4] 결과 요약
    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total_tests}개")
    print(f"통과: {passed_tests}개")
    print(f"실패: {len(failed_cases)}개")

    if failed_cases:
        print("\n실패 케이스:")
        for case_id, reason in failed_cases:
            print(f"- {case_id}: {reason}")


# ==========================================
# [보너스] 1D vs 2D 메모리 접근 성능 비교 모드
# ==========================================
def run_bonus_benchmark():
    print("\n#---------------------------------------")
    print("# [보너스] 2D vs 1D 배열 MAC 연산 속도 비교 (1000회 평균)")
    print("#---------------------------------------")
    print(f"{'크기':<8} {'2D 평균(ms)':<15} {'1D 평균(ms)':<15} {'개선율':<10}")
    print("-" * 52)
    for n in [3, 5, 13, 25, 50]:
        mat_a, mat_b = generate_patterns(n)
        flat_a = flatten_matrix(mat_a)
        flat_b = flatten_matrix(mat_b)

        t0 = time.perf_counter()
        for _ in range(1000):
            mac_2d(mat_a, mat_b)
        t_2d = ((time.perf_counter() - t0) / 1000) * 1000

        t0 = time.perf_counter()
        for _ in range(1000):
            mac_1d(flat_a, flat_b)
        t_1d = ((time.perf_counter() - t0) / 1000) * 1000

        speedup = ((t_2d - t_1d) / t_2d) * 100 if t_2d > 0 else 0
        size_str = f"{n}x{n}"
        print(f"{size_str:<8} {t_2d:<15.5f} {t_1d:<15.5f} {speedup:>6.1f}%")


def main():
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. [보너스] 1D vs 2D 메모리 최적화 벤치마크")

    choice = input("선택: ").strip()
    if choice == "1":
        run_mode_1()
    elif choice == "2":
        run_mode_2(DATA_PATH)
    elif choice == "3":
        run_bonus_benchmark()
    else:
        print("잘못된 선택입니다. 1, 2, 3 중 하나를 입력하세요.")


if __name__ == "__main__":
    main()
