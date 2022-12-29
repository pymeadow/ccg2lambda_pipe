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
            kwargs = spec["kwargs"]
            class_module = importlib.import_module(module_name)
            step_object = getattr(class_module, class_name)(**kwargs)
            pipe_steps.append((name, step_object))
        
        return Pipeline(pipe_steps)

if __name__ == "__main__":
    pipe_spec = dict(
        reader=dict(module="ccg2lamp.pipelines.step_corpus_io",
                    klass="CorpusReader",
                    kwargs={}),
        writer=dict(module="ccg2lamp.pipelines.step_corpus_io",
                    klass="CorpusWriter",
                    kwargs=dict(output_suffix="foo.bar"))
    )
    
    pipe_factory = PipeFactory()
    pipe = pipe_factory.transform(pipe_spec)
    print(pipe) 