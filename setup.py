from setuptools import setup, find_packages


setup(
    name="cortex-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain-openai",
        "langchain-ollama",
        "ddgs",
    ],
    description="Κ layer: critic externo para agentes de IA. Sabe cuándo no actuar.",
    author="Jairogelpi",
    license="MIT",
)