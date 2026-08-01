"""
smoke_test_homepage.py — Smoke test for PROMO card visibility in GUI.
Runs headless (QT_QPA_PLATFORM=offscreen) and verifies products render.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Must set QT_QPA_PLATFORM before QApplication
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
from PyQt6.QtCore import QTimer
import data_manager

def main():
    app = QApplication(sys.argv)

    # Load fonts if available (same as main.py)
    from PyQt6.QtGui import QFontDatabase
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Fonts")
    for fname in ["GoogleSans-Regular.ttf", "GoogleSans-Bold.ttf"]:
        fpath = os.path.join(font_dir, fname)
        if os.path.exists(fpath):
            QFontDatabase.addApplicationFont(fpath)

    # Apply palette (same as main.py)
    from PyQt6.QtGui import QPalette, QColor
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#191919"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#191919"))
    pal.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor("#191919"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#21C083"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(pal)

    # Import after QT_QPA_PLATFORM is set
    import gui_pyqt

    # Create MainWindow
    window = gui_pyqt.MainWindow()
    window.show()  # Required for widget geometry to be valid in offscreen mode

    # Wait for initial refresh to complete
    # QTimer.singleShot(0, self.refresh) fires after event loop starts
    # We need to process events and wait for refresh

    def check_and_verify():
        # Access home_w (HomePage) which is page 0
        home = window.home_w

        # Force refresh (same as what QTimer does)
        home.refresh()

        # Process events to ensure rendering
        app.processEvents()

        # Now check product_grid
        grid = home.product_grid
        if grid is None:
            print("FAIL: product_grid is None")
            app.exit(1)
            return

        # Count PROMO cards
        promo_card_count = 0
        total_cards = 0
        for i in range(grid.count()):
            item = grid.itemAt(i)
            if item and item.widget():
                card = item.widget()
                # ProductListItem has promo_overlay attribute when has_actual_discount
                if hasattr(card, 'promo_overlay') and card.promo_overlay is not None:
                    promo_card_count += 1
                total_cards += 1

        print(f"Total cards in grid: {total_cards}")
        print(f"PROMO cards detected: {promo_card_count}")

        if total_cards == 0:
            print("FAIL: No cards rendered in product_grid")
            app.exit(1)
            return

        if promo_card_count == 0:
            print("FAIL: No PROMO cards detected (all REGULER)")
            app.exit(1)
            return

        print(f"PASS: {promo_card_count}/{total_cards} cards have PROMO badges")

        # Save screenshot of product_grid
        try:
            if hasattr(home, 'product_container'):
                screenshot = home.product_container.grab()
                screenshot.save(r"C:\Users\Arya\.omo\evidence\task-8-homepage-screenshot.png")
                print(f"Screenshot saved: task-8-homepage-screenshot.png ({screenshot.width()}x{screenshot.height()})")
        except Exception as e:
            print(f"WARNING: Could not save screenshot 1: {e}")

        # Save final screenshot
        try:
            final_ss = window.grab()
            final_ss.save(r"C:\Users\Arya\.omo\evidence\task-9-homepage-final.png")
            print(f"Final screenshot saved: task-9-homepage-final.png ({final_ss.width()}x{final_ss.height()})")
        except Exception as e:
            print(f"WARNING: Could not save final screenshot: {e}")

        print("ALL CHECKS PASSED")
        app.exit(0)

    # Schedule check after event loop starts (same pattern as QTimer.singleShot(0, ...))
    QTimer.singleShot(100, check_and_verify)

    # Run event loop briefly
    app.exec()

    # Exit with code from check_and_verify
    return

if __name__ == "__main__":
    main()