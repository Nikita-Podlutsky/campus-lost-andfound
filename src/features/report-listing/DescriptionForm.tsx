import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';

export interface DescriptionFormValues {
  title: string;
  description: string;
  location: string;
}

interface DescriptionFormProps {
  values: DescriptionFormValues;
  onChange: (values: DescriptionFormValues) => void;
}

export function DescriptionForm({ values, onChange }: DescriptionFormProps) {
  function handleField<K extends keyof DescriptionFormValues>(field: K, value: string) {
    onChange({ ...values, [field]: value });
  }

  return (
    <Stack spacing={2}>
      <TextField
        label="Короткое название"
        placeholder="Например, 'какая то вещь' пусть"
        value={values.title}
        onChange={(e) => handleField('title', e.target.value)}
        required
        fullWidth
      />
      <TextField
        label="Описание"
        placeholder="Опишите вещь и приметы"
        value={values.description}
        onChange={(e) => handleField('description', e.target.value)}
        required
        fullWidth
        multiline
        minRows={3}
      />
      <TextField
        label="Место находки (детально)"
        placeholder="Например, под столом, на подоконнике у окна"
        helperText="Точка на карте определяется по геолокации - здесь опишите точнее, где именно"
        value={values.location}
        onChange={(e) => handleField('location', e.target.value)}
        required
        fullWidth
      />
    </Stack>
  );
}
