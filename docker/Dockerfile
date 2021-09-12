FROM continuumio/miniconda3

RUN conda update conda && conda install pip

COPY environment.yml /tmp/environment.yml
RUN conda env update -f /tmp/environment.yml -n base && rm /tmp/environment.yml

COPY . /tmp/stactools-goes
RUN cd /tmp/stactools-goes && pip install . && rm -rf /tmp/stactools-goes

ENV PYTHONPATH=/src/stactools-goes/src:$PYTHONPATH

ENTRYPOINT [ "python", "-m", "stactools.cli" ]
