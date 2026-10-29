import { Input as InputBase } from './Input';
import { Password } from './Password';
import { TextArea } from './TextArea';

export const Input = Object.assign(InputBase, { TextArea, Password });
export type { InputProps } from './Input';
