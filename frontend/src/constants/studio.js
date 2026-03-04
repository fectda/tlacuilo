export const SHOT_TYPES = [
    { value: 'macro', icon: '⌀', label: 'Macro', desc: 'Close-up extremo de un componente: junta de soldadura, conector, área de PCB.' },
    { value: 'context', icon: '◫', label: 'Context', desc: 'Plano medio o abierto que muestra el objeto en su entorno de operación real.' },
    { value: 'conceptual', icon: '◈', label: 'Conceptual', desc: 'Toma abstracta que comunica el concepto central del proyecto (escala, power glow, contraste orgánico vs. electrónico).' },
    { value: 'screenshot', icon: '▣', label: 'Screenshot', desc: 'Evidencia digital de interfaces de software, fragmentos de código o visualizaciones de datos.' },
]

export const ATMOSPHERES = [
    { value: 'rojo', dot: '#D4442F', label: 'Rojo', desc: 'Estados activos, encendido, componentes de alta energía (LEDs, rieles de poder, soldadura).' },
    { value: 'turquesa', dot: '#00A6B6', label: 'Turquesa', desc: 'Estados idle, RF/datos, sensores, partes electrónicas de precisión.' },
    { value: 'ambar', dot: '#F59E0B', label: 'Ámbar', desc: 'Eventos térmicos, materiales orgánicos, contextos vintage o cálidos.' },
]

export const SHOT_STATUS_CONFIG = {
    pending_upload: { label: 'PENDING UPLOAD', textColor: '#6b7280', dotColor: '#4b5563' },
    queued: { label: 'QUEUED', textColor: '#f59e0b', dotColor: '#f59e0b' },
    generated: { label: 'GENERATED', textColor: '#10b981', dotColor: '#10b981' },
    approved: { label: 'APPROVED ✓', textColor: '#22d3ee', dotColor: '#22d3ee' },
}

export const ATMOSPHERE_STYLES = {
    rojo: { bg: 'rgba(212,68,47,0.25)', text: '#f87171', border: 'rgba(212,68,47,0.4)', accent: '#D4442F' },
    turquesa: { bg: 'rgba(0,166,182,0.2)', text: '#22d3ee', border: 'rgba(0,166,182,0.4)', accent: '#00A6B6' },
    ambar: { bg: 'rgba(245,158,11,0.2)', text: '#fbbf24', border: 'rgba(245,158,11,0.4)', accent: '#F59E0B' },
}
