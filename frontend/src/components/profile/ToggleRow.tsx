interface Props {
  label: string;
  sublabel?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export default function ToggleRow({ label, sublabel, checked, onChange }: Props) {
  return (
    <div className="toggle-row">
      <div className="toggle-label">
        <span>{label}</span>
        {sublabel && <small>{sublabel}</small>}
      </div>
      <label className="toggle-switch">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span className="toggle-slider"></span>
      </label>
    </div>
  );
}