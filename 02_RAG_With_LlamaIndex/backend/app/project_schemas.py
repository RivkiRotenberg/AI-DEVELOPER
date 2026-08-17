from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ----------------------------------------------------
# סכמות משניות עבור מקור המידע
# ----------------------------------------------------
class SourceMetadata(BaseModel):
    file_path: str = Field(description="הנתיב היחסי או המלא של קובץ ה-Markdown")
    line_range: List[int] = Field(description="טווח השורות בקובץ שבו המידע מופיע, לדוגמה [10, 25]")
    section_anchor: Optional[str] = Field(None, description="הכותרת או ה-Anchor הקרוב ביותר, לדוגמה ## UI Rules")

# ----------------------------------------------------
# סכמות עבור שלושת סוגי הפריטים
# ----------------------------------------------------
class DecisionItem(BaseModel):
    id: str = Field(description="מזהה ייחודי, לדוגמה dec-001")
    title: str = Field(description="כותרת קצרה של ההחלטה הטכנולוגית")
    summary: str = Field(description="פירוט ותמצית ההחלטה שהתקבלה")
    tags: List[str] = Field(default=[], description="תגיות רלוונטיות, לדוגמה ['db', 'backend']")
    source: SourceMetadata
    updated_at: datetime = Field(description="תאריך וזמן עדכון ההחלטה (ISO format)")

class RuleItem(BaseModel):
    id: str = Field(description="מזהה ייחודי, לדוגמה rule-001")
    rule: str = Field(description="הכלל או ההנחיה המדויקת לפיתוח")
    scope: str = Field(description="טווח ההשפעה של הכלל, לדוגמה: ui, backend, auth")
    source: SourceMetadata
    updated_at: datetime = Field(description="תאריך וזמן עדכון הכלל (ISO format)")

class WarningItem(BaseModel):
    id: str = Field(description="מזהה ייחודי, לדוגמה warn-001")
    area: str = Field(description="האזור הרגיש במערכת, לדוגמה: environment variables, deployment")
    message: str = Field(description="תוכן האזהרה או הדגש הקריטי")
    severity: str = Field(description="רמת חומרה: low, medium, high")
    source: SourceMetadata
    updated_at: datetime = Field(description="תאריך וזמן זיהוי האזהרה (ISO format)")

# ----------------------------------------------------
# הסכמה הראשית של שכבת המידע המובנית
# ----------------------------------------------------
class ProjectStructuredData(BaseModel):
    schema_version: str = Field(default="1.0")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # שלושת סוגי הפריטים הנדרשים
    decisions: List[DecisionItem] = Field(default=[])
    rules: List[RuleItem] = Field(default=[])
    warnings: List[WarningItem] = Field(default=[])