import importlib

from typing import Dict

from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin

class PipeFactory(TransformerMixin):
    """factory to construct pipelines from dictionary"""
    def __init__(self):
        pass
    
    def transform(self, pipe_spec: Dict) -> Pipeline:
        
        pipe_steps = []
        for name, spec in pipe_spec.items():
            module_name = spec["module"]
            class_name = spec["klass"]
            args = spec.get("args", [])
            kwargs = spec.get("kwargs", {})
            class_module = importlib.import_module(module_name)
            step_object = getattr(class_module, class_name)(*args, **kwargs)
            pipe_steps.append((name, step_object))
        
        return Pipeline(pipe_steps)

if __name__ == "__main__":
    import json

    pipe_spec = dict(
        reader=dict(module="ccg2lamp.pipelines.step_corpus_io",
                    klass="CorpusReader",
                    kwargs={}),
        writer=dict(module="ccg2lamp.pipelines.step_corpus_io",
                    klass="CorpusWriter",
                    kwargs=dict(output_suffix="foo.bar"))
    )
    print(pipe_spec)

    pipe_factory = PipeFactory()
    pipe_1 = pipe_factory.transform(pipe_spec)
    print(pipe_1)
    
    # test loading spec from json
    with open("/tmp/pipe_spec.json", "w") as out_file:
        json.dump(pipe_spec, out_file)
    with open("/tmp/pipe_spec.json", "r") as in_file:
        pipe_spec = json.load(in_file)
    pipe_2 = pipe_factory.transform(pipe_spec)
    print(pipe_2)
    steps_1 = [n for n, s in pipe_1.steps]
    steps_2 = [n for n, s in pipe_2.steps]
    assert steps_1 == steps_2