import { CROPS } from "@/lib/constants";

interface Props {
  selected: string;
  onChange: (crop: string) => void;
}

export default function CropSelector({ selected, onChange }: Props) {
  return (
    <div className="crop-selector">
      {CROPS.map((crop) => (
        <span
          key={crop}
          className={`crop-option${selected === crop ? " selected" : ""}`}
          onClick={() => onChange(crop)}
        >
          {crop}
        </span>
      ))}
    </div>
  );
}