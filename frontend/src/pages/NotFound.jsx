import { Button, EmptyState } from '../components/ui'
export default function NotFound() {
  return <div className="mx-auto max-w-2xl px-4 py-20"><EmptyState title="Page not found" text="That page doesn't exist or was moved." action={<Button to="/">Back to home</Button>} /></div>
}
