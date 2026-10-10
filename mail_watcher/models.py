from dataclasses import dataclass, field


@dataclass(frozen=True)
class IncomingMail:
    uid: str
    from_addr: str
    from_name: str
    subject: str
    date: str
    body: str
    in_reply_to: str
    references: str
    attachments: tuple[str, ...] = field(default_factory=tuple)
