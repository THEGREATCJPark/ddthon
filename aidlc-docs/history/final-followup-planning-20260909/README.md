# Planning diagnostics, not repaired results

Current main was inspected without changing application/test source. A single existing test was executed with Python UTF-8 mode disabled in a Korean cp949 locale; it failed because its generated UTF-8 pip.ini contains an unescaped Korean path. A pip --version probe returned exit2 and explicitly identified invalid cp949 configuration characters. This is not a fresh full-suite 199/1/2 result.

The independent malformed-JSON store probe produced an unhandled CLI traceback with exit1, without changing the store. These are pre-fix diagnostic results only. No original user data, installed package, network remote or product source was modified by the probes.

An earlier diagnostic with PYTHONIOENCODING=utf-8 also produced a subprocess decoding warning. That extra output override was removed for the native cp949 reproduction archived here; the earlier operator log remains outside this submission archive and is not presented as an additional product defect.
