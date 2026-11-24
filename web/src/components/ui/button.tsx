import * as React from 'react';
import {Slot} from '@radix-ui/react-slot';
import {clsx} from 'clsx';
import {twMerge} from 'tailwind-merge';
export const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & {asChild?: boolean; variant?: 'default' | 'outline' | 'ghost'}>(({className, asChild = false, variant = 'default', ...props}, ref) => {
  const Component = asChild ? Slot : 'button';
  return <Component ref={ref} className={twMerge(clsx('btn', variant !== 'default' && variant, className))} {...props}/>;
});
Button.displayName = 'Button';
