#!/usr/bin/env python3
"""
daily_contributions.py
Tự động tính toán tọa độ trên GitHub Contribution Graph và thực hiện commit mỗi ngày:
- Năm 2027: Vẽ chữ "noqokhxnh" (6 commits/ngày trên các điểm chữ, 1 commit/ngày thường).
- Ngoài năm 2027: Duy trì 1 commit/ngày như hiện tại.
"""

import argparse
import datetime
import os
import subprocess
import sys

TARGET_YEAR = 2027

# Bảng font chữ In Hoa (5 hàng: Thứ 2 -> Thứ 6)
FONT_UPPER = {
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '.##.'],
    'Q': ['.##.', '#..#', '#..#', '#.#.', '.###'],
    'K': ['#..#', '#.#.', '##..', '#.#.', '#..#'],
    'H': ['#..#', '#..#', '####', '#..#', '#..#'],
    'X': ['#..#', '.##.', '.##.', '.##.', '#..#']
}

# Bảng font chữ In Thường (7 hàng: Chủ nhật -> Thứ 7)
FONT_LOWER = {
    'n': ['    ', '    ', '### ', '#  #', '#  #', '#  #', '    '],
    'o': ['    ', '    ', ' ## ', '#  #', '#  #', ' ## ', '    '],
    'q': ['    ', '    ', ' ###', '#  #', ' ###', '   #', '   #'],
    'k': ['#   ', '#   ', '#  #', '### ', '#  #', '#  #', '    '],
    'h': ['#   ', '#   ', '### ', '#  #', '#  #', '#  #', '    '],
    'x': ['    ', '    ', '#  #', ' ## ', ' ## ', '#  #', '    ']
}


def get_first_sunday_of_year(year: int) -> datetime.date:
    """Trả về ngày Chủ Nhật bắt đầu của Cột 0 trên GitHub Contribution Graph."""
    jan1 = datetime.date(year, 1, 1)
    jan1_dow = (jan1.weekday() + 1) % 7  # 0=Sun, 1=Mon, ..., 6=Sat
    return jan1 - datetime.timedelta(days=jan1_dow)


def get_github_coords(d: datetime.date):
    """Trả về (col, row) trên lưới GitHub (col: 0..52, row: 0..6 với 0=Sun)."""
    first_sun = get_first_sunday_of_year(d.year)
    col = (d - first_sun).days // 7
    row = (d.weekday() + 1) % 7
    return col, row


def build_grid(style: str = 'UPPERCASE', year: int = TARGET_YEAR):
    """Tạo ma trận boolean 7 hàng x 53 cột cho chữ noqokhxnh."""
    grid = [[False] * 53 for _ in range(7)]
    style_upper = style.upper()

    if style_upper == 'UPPERCASE':
        word = 'NOQOKHXNH'
        lines = ['' for _ in range(5)]
        for ch in word:
            for r in range(5):
                lines[r] += FONT_UPPER[ch][r] + '.'
        total_w = len(lines[0].rstrip('.'))
        left_pad = (53 - total_w) // 2

        for r in range(5):
            line = lines[r].rstrip('.')
            for c_offset, ch in enumerate(line):
                col = left_pad + c_offset
                if ch == '#' and 0 <= col < 53:
                    grid[r + 1][col] = True  # Hàng 1..5 tương ứng Mon..Fri

    elif style_upper == 'LOWERCASE':
        word = 'noqokhxnh'
        lines = ['' for _ in range(7)]
        for ch in word:
            for r in range(7):
                lines[r] += FONT_LOWER[ch][r] + ' '
        total_w = len(lines[0].rstrip())
        left_pad = (53 - total_w) // 2

        for r in range(7):
            line = lines[r].rstrip()
            for c_offset, ch in enumerate(line):
                col = left_pad + c_offset
                if ch == '#' and 0 <= col < 53:
                    grid[r][col] = True

    return grid


def get_commit_count_for_date(d: datetime.date, style: str = 'UPPERCASE',
                              pattern_commits: int = 6, normal_commits: int = 1):
    """Xác định số lượng commit cần thiết cho một ngày cụ thể."""
    if d.year != TARGET_YEAR:
        return normal_commits, False, (-1, -1)

    grid = build_grid(style, TARGET_YEAR)
    col, row = get_github_coords(d)

    if 0 <= col < 53 and 0 <= row < 7 and grid[row][col]:
        return pattern_commits, True, (col, row)
    return normal_commits, False, (col, row)


def preview_pattern(style: str = 'UPPERCASE', year: int = TARGET_YEAR):
    """In bản đồ đóng góp cả năm dạng ASCII và Emoji trực quan."""
    first_sun = get_first_sunday_of_year(year)
    grid = build_grid(style, year)

    # Tạo hàng tiêu đề các tháng
    month_cols = {}
    for m in range(1, 13):
        d = datetime.date(year, m, 1)
        col = (d - first_sun).days // 7
        month_cols[col] = d.strftime('%b')

    header = [' '] * 53
    for col, name in sorted(month_cols.items()):
        for i, ch in enumerate(name):
            if col + i < 53:
                header[col + i] = ch

    day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    print(f"\nBẢN ĐỒ GITHUB CONTRIBUTION GRAPH NĂM {year} (Style: {style})")
    print("=" * 65)
    print("      " + ''.join(header))

    total_pattern_days = 0
    total_normal_days = 0
    first_pattern_day = None
    last_pattern_day = None

    for r in range(7):
        chars = []
        for c in range(53):
            curr_d = first_sun + datetime.timedelta(days=c * 7 + r)
            if curr_d.year != year:
                chars.append(' ')
            elif grid[r][c]:
                chars.append('#')
                total_pattern_days += 1
                if first_pattern_day is None or curr_d < first_pattern_day:
                    first_pattern_day = curr_d
                if last_pattern_day is None or curr_d > last_pattern_day:
                    last_pattern_day = curr_d
            else:
                chars.append('.')
                total_normal_days += 1
        print(f"{day_names[r]:4s}: " + ''.join(chars))

    print("=" * 65)
    print(f"Thống kê năm {year}:")
    print(f"  - Tổng số ngày: {total_pattern_days + total_normal_days} ngày")
    print(f"  - Ngày tạo chữ (#): {total_pattern_days} ngày (xanh đậm nhất)")
    print(f"  - Ngày nền (.): {total_normal_days} ngày (xanh nhạt)")
    if first_pattern_day and last_pattern_day:
        print(f"  - Bắt đầu chữ cái: {first_pattern_day.strftime('%d/%m/%Y (%A)')}")
        print(f"  - Kết thúc chữ cái: {last_pattern_day.strftime('%d/%m/%Y (%A)')}")
    print()


def ensure_git_config():
    """Đảm bảo git user và email được cấu hình nếu chưa có."""
    name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    if not name:
        subprocess.run(["git", "config", "user.name", "noqokhxnh"], check=False)
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True).stdout.strip()
    if not email:
        subprocess.run(["git", "config", "user.email", "khanh2k5xxx@gmail.com"], check=False)


def count_existing_commits_today(log_path: str, date_str: str) -> int:
    """Đếm số commit đã được ghi nhận trong file activity.log cho ngày hôm nay."""
    if not os.path.exists(log_path):
        return 0
    count = 0
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith(date_str):
                count += 1
    return count


def execute_daily_commits(style: str = 'UPPERCASE', pattern_commits: int = 6,
                         normal_commits: int = 1, force: bool = False,
                         dry_run: bool = False, custom_date: str = None):
    """Thực hiện commit cho ngày hôm nay (hoặc custom_date)."""
    if custom_date:
        today = datetime.datetime.strptime(custom_date, "%Y-%m-%d").date()
    else:
        today = datetime.datetime.now(datetime.timezone.utc).date()

    date_str = today.strftime("%Y-%m-%d")
    target_commits, is_pattern, coords = get_commit_count_for_date(
        today, style=style, pattern_commits=pattern_commits, normal_commits=normal_commits
    )

    log_dir = "assets"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "activity.log")

    existing_count = count_existing_commits_today(log_path, date_str)
    print(f"📅 Ngày kiểm tra: {date_str} (UTC)")
    print(f"🎯 Điểm ảnh chữ: {'CÓ (Pixel Art)' if is_pattern else 'KHÔNG (Ngày thường)'} {coords if is_pattern else ''}")
    print(f"🔢 Số commit mục tiêu: {target_commits} | Đã ghi nhận hôm nay: {existing_count}")

    if existing_count >= target_commits and not force:
        print("✅ Ngày hôm nay đã đạt đủ số commit mục tiêu.")
        status = subprocess.run(["git", "status", "--porcelain", "assets/"], capture_output=True, text=True).stdout.strip()
        if status:
            print("📦 Phát hiện thay đổi trong assets/ (SVGs), tiến hành commit bổ sung...")
            subprocess.run(["git", "add", "assets/"], check=True)
            subprocess.run(["git", "commit", "-m", f"📈 Update GitHub stats [{date_str}] [skip ci]"], check=True)
        return

    commits_to_make = target_commits if force else (target_commits - existing_count)
    print(f"🚀 Tiến hành thực hiện {commits_to_make} commit...")

    if dry_run:
        print("🔍 [DRY-RUN] Không ghi file hoặc commit thật.")
        return

    ensure_git_config()

    for i in range(1, commits_to_make + 1):
        commit_idx = (existing_count + i) if not force else i
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        status_desc = f"Pattern pixel {coords}" if is_pattern else "Daily background"
        log_entry = f"{now_str} | {date_str} | commit {commit_idx}/{target_commits} | {status_desc}\n"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        # Stage assets directory
        subprocess.run(["git", "add", "assets/"], check=True)

        if is_pattern:
            msg = f"🎨 Daily contribution [{commit_idx}/{target_commits}] - {date_str} [skip ci]"
        else:
            msg = f"📈 Daily update {date_str} [{commit_idx}/{target_commits}] [skip ci]"

        commit_cmd = ["git", "commit", "-m", msg]
        # Nếu test ngày tùy chỉnh, đặt thêm biến môi trường ngày tác giả
        env = os.environ.copy()
        if custom_date:
            fake_time = f"{date_str}T12:{i:02d}:00Z"
            env["GIT_AUTHOR_DATE"] = fake_time
            env["GIT_COMMITTER_DATE"] = fake_time

        result = subprocess.run(commit_cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ [{commit_idx}/{target_commits}] {msg}")
        else:
            print(f"  ⚠️ Commit warning: {result.stderr.strip() or result.stdout.strip()}")

    print(f"✨ Hoàn tất {commits_to_make} commit cho ngày {date_str}!")


def backfill_entire_year(style: str = 'UPPERCASE', pattern_commits: int = 6,
                         normal_commits: int = 1, dry_run: bool = False, year: int = TARGET_YEAR):
    """Backfill toàn bộ 365 ngày của năm chỉ định với author date tương ứng."""
    print(f"⚠️ Đang chuẩn bị backfill toàn bộ năm {year}...")
    first_day = datetime.date(year, 1, 1)
    last_day = datetime.date(year, 12, 31)
    num_days = (last_day - first_day).days + 1

    for day_offset in range(num_days):
        d = first_day + datetime.timedelta(days=day_offset)
        execute_daily_commits(
            style=style,
            pattern_commits=pattern_commits,
            normal_commits=normal_commits,
            force=True,
            dry_run=dry_run,
            custom_date=d.strftime("%Y-%m-%d")
        )


def main():
    parser = argparse.ArgumentParser(description="Quản lý commit vẽ chữ trên GitHub Contribution Graph.")
    parser.add_argument("--run", action="store_true", help="Chạy commit cho ngày hôm nay (dùng trong CI)")
    parser.add_argument("--preview", action="store_true", help="Xem trước lưới biểu đồ đóng góp của năm")
    parser.add_argument("--style", choices=["UPPERCASE", "LOWERCASE"],
                        default=os.getenv("PATTERN_STYLE", "UPPERCASE"),
                        help="Phong cách chữ (UPPERCASE hoặc LOWERCASE)")
    parser.add_argument("--pattern-commits", type=int,
                        default=int(os.getenv("PATTERN_COMMITS", "6")),
                        help="Số commit vào ngày chữ cái (mặc định: 6)")
    parser.add_argument("--normal-commits", type=int,
                        default=int(os.getenv("NORMAL_COMMITS", "1")),
                        help="Số commit vào ngày thường (mặc định: 1)")
    parser.add_argument("--test-date", type=str, help="Kiểm tra một ngày cụ thể (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Bỏ qua kiểm tra trùng lặp commit")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử không ghi commit")
    parser.add_argument("--backfill-year", type=int, help="Backfill toàn bộ commit cho năm chỉ định")

    args = parser.parse_args()

    if args.preview:
        preview_pattern(style=args.style)
    elif args.test_date:
        d = datetime.datetime.strptime(args.test_date, "%Y-%m-%d").date()
        target, is_p, coords = get_commit_count_for_date(d, style=args.style,
                                                         pattern_commits=args.pattern_commits,
                                                         normal_commits=args.normal_commits)
        print(f"Kiểm tra ngày: {d.strftime('%Y-%m-%d (%A)')}")
        print(f"Cột/Hàng: Cột {coords[0]}, Hàng {coords[1]}")
        print(f"Loại: {'Pixel chữ (Xanh đậm)' if is_p else 'Ngày thường (Xanh nhạt)'}")
        print(f"Số commit: {target}")
    elif args.backfill_year:
        backfill_entire_year(style=args.style, pattern_commits=args.pattern_commits,
                             normal_commits=args.normal_commits, dry_run=args.dry_run,
                             year=args.backfill_year)
    elif args.run:
        execute_daily_commits(style=args.style, pattern_commits=args.pattern_commits,
                              normal_commits=args.normal_commits, force=args.force,
                              dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
