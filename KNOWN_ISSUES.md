# KNOWN_ISSUES.md

## Spirit Hatch - Build Issues Log

Issues discovered during development and testing.

---

## 🔴 Critical Issues

### Issue #001 - Evolution Stage Skipping
**Status:** FIXED

Under specific conditions, the spirit could skip evolution stages entirely (e.g., Hatchling → Mature Spirit).

**Cause:** Race condition when stats updated simultaneously with day counter.  
**Fix:** Added evolution stage verification lock.

---

### Issue #002 - Negative Health Recovery
**Status:** FIXED

When health dropped below 10%, the `rest` command sometimes decreased health instead of restoring it.

**Cause:** Integer overflow in percentage-based recovery calculation.  
**Fix:** Changed to absolute values with floor check.

---

## 🟡 High Priority Issues

### Issue #003 - Terminal Width Crash
**Status:** OPEN

Game crashes when terminal width < 46 characters.

**Workaround:** Keep terminal at least 50 characters wide.  
**Proposed Fix:** Add width detection at startup.

---

### Issue #004 - Time Travel Exploit
**Status:** FIXED

Players could change system clock to instantly age their spirit.

**Fix:** Implemented session-based time tracking instead of relying on system time.

---

### Issue #005 - Emoji Rendering (Windows)
**Status:** PARTIAL FIX

Emojis render as boxes/question marks on older Windows terminals.

**Workaround:** Use Windows Terminal or PowerShell 7+.

---

## 🟢 Medium Priority Issues

### Issue #006 - Stat Bar Overflow at 100%
**Status:** FIXED

Status bars misaligned when stats reached exactly 100%.

**Fix:** Updated string formatting for triple-digit percentages.

---

### Issue #007 - Evolution Spam
**Status:** FIXED

Spamming `evolve` command caused duplicate messages.

**Fix:** Added 2-second cooldown after evolution.

---

### Issue #008 - Decimal Precision Display
**Status:** OPEN

Stats sometimes show excessive decimals (e.g., "47.3333333334%").

**Impact:** Visual only, doesn't affect gameplay.

---

## 🔵 Low Priority Issues

### Issue #009 - No Command History
**Status:** WONTFIX

Arrow keys don't recall previous commands.

**Reason:** Out of scope for v1.0.

---

### Issue #010 - No Quit Confirmation
**Status:** OPEN

`quit` exits immediately without "Are you sure?" prompt.

**Planned:** v1.1 update.

---

## 📊 Summary

- **Total Issues:** 10
- **Critical:** 2 (both fixed)
- **High:** 3 (2 fixed, 1 open)
- **Medium:** 3 (2 fixed, 1 open)
- **Low:** 2 (1 open, 1 wontfix)

**Critical/High Fix Rate:** 80%

---

*Last Updated: 2024-02-15*
