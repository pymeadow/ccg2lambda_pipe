
#Traceback (most recent call last):
#  File "<input>", line 1, in <module>
#  File "C:\Users\User\AppData\Local\Programs\Python\Python310\lib\site-packages\nltk\sem\logic.py", line 160, in parse
#    result.typecheck(signature)
#  File "C:\Users\User\AppData\Local\Programs\Python\Python310\lib\site-packages\nltk\sem\logic.py", line 1057, in typecheck
#    self._set_type(signature=sig)
#  File "C:\Users\User\AppData\Local\Programs\Python\Python310\lib\site-packages\nltk\sem\logic.py", line 1861, in _set_type
#    self.second._set_type(TRUTH_TYPE, signature)
#  File "C:\Users\User\AppData\Local\Programs\Python\Python310\lib\site-packages\nltk\sem\logic.py", line 1699, in _set_type
#    self.term._set_type(other_type.second, signature)


from nltk.sem.logic import LogicParser
tlp = LogicParser(True)
tlp.parse(r"P & \y.Q")
#tlp.parse(r"P(x) & \y.Q(y)")
#tlp.parse(r"P(x, y) & \a.Q(a)")
#tlp.parse(r"\x. P(x) & \y. Q(y)")
#tlp.parse(r"\x. P(x) | \y. Q(y)")
#tlp.parse(r"P -> \x. Q(x)")
#tlp.parse(r"-\x. P(x)")