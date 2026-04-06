from dataclasses import dataclass


@dataclass
class Job:
    title: str
    company: str
    location: str
    link: str
    description: str
    source: str