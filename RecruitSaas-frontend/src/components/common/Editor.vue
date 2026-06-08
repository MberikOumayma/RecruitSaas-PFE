<template>
  <div v-if="editor" class="editor-container">
    <div class="editor-toolbar">
      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('bold') }" 
        @click="editor.chain().focus().toggleBold().run()"
        title="Bold"
      >
        <BoldIcon :size="16" />
      </button>
      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('italic') }" 
        @click="editor.chain().focus().toggleItalic().run()"
        title="Italic"
      >
        <ItalicIcon :size="16" />
      </button>
      
      <div class="toolbar-divider"></div>

      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" 
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        title="Heading 2"
      >
        <Heading2Icon :size="16" />
      </button>
      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" 
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        title="Heading 3"
      >
        <Heading3Icon :size="16" />
      </button>

      <div class="toolbar-divider"></div>

      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('bulletList') }" 
        @click="editor.chain().focus().toggleBulletList().run()"
        title="Bullet List"
      >
        <ListIcon :size="16" />
      </button>
      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('orderedList') }" 
        @click="editor.chain().focus().toggleOrderedList().run()"
        title="Ordered List"
      >
        <ListOrderedIcon :size="16" />
      </button>

      <div class="toolbar-divider"></div>

      <button 
        type="button"
        class="toolbar-btn" 
        :class="{ 'is-active': editor.isActive('link') }" 
        @click="setLink"
        title="Insert Link"
      >
        <LinkIcon :size="16" />
      </button>

      <button 
        type="button"
        class="toolbar-btn btn-clear" 
        @click="editor.chain().focus().unsetAllMarks().clearNodes().run()"
        title="Clear Formatting"
      >
        <EraserIcon :size="16" />
      </button>
    </div>
    
    <editor-content :editor="editor" class="editor-content" />
  </div>
</template>

<script>
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import {
  BoldIcon,
  ItalicIcon,
  Heading2Icon,
  Heading3Icon,
  ListIcon,
  ListOrderedIcon,
  LinkIcon,
  EraserIcon
} from 'lucide-vue-next'

export default {
  name: 'RichTextEditor',
  components: {
    EditorContent,
    BoldIcon,
    ItalicIcon,
    Heading2Icon,
    Heading3Icon,
    ListIcon,
    ListOrderedIcon,
    LinkIcon,
    EraserIcon
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Write something...'
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      editor: null
    }
  },
  watch: {
    modelValue(value) {
      const isSame = this.editor.getHTML() === value
      if (isSame) return
      this.editor.commands.setContent(value, false)
    }
  },
  mounted() {
    this.editor = new Editor({
      content: this.modelValue,
      extensions: [
        StarterKit.configure({
          heading: {
            levels: [2, 3]
          }
        }),
        Link.configure({
          openOnClick: false,
          HTMLAttributes: {
            class: 'editor-link',
          },
        }),
        Placeholder.configure({
          placeholder: this.placeholder,
        }),
      ],
      editorProps: {
    transformPastedHTML(html) {
  return html
    .replace(/<li>\s*<p>(.*?)<\/p>\s*<\/li>/g, '<li>$1</li>')
    .replace(/<p>\s*<\/p>/g, '')
    .replace(/<p>(.*?)<\/p>/g, '$1')
    .replace(/<br\s*\/?>/g, '')
    .replace(/style="[^"]*"/g, '')
}
  },
      onUpdate: () => {
        this.$emit('update:modelValue', this.editor.getHTML())
      },
    })
  },
  beforeUnmount() {
    this.editor.destroy()
  },
  methods: {
    setLink() {
      const previousUrl = this.editor.getAttributes('link').href
      const url = window.prompt('URL', previousUrl)

      // cancelled
      if (url === null) {
        return
      }

      // empty
      if (url === '') {
        this.editor.chain().focus().extendMarkRange('link').unsetLink().run()
        return
      }

      const { from, to, empty } = this.editor.state.selection

      // If nothing is selected, we insert the URL directly as text, link it, and move cursor forward
      if (empty) {
        this.editor
          .chain()
          .focus()
          .insertContent(url)
          .setTextSelection({ from, to: from + url.length })
          .setLink({ href: url })
          .setTextSelection(from + url.length)
          .unsetLink()
          .insertContent('\u00A0') // insert a non-breaking space after to separate
          .run()
        return
      }

      // update link and move cursor to the end so user can keep typing normally
      this.editor
        .chain()
        .focus()
        .extendMarkRange('link')
        .setLink({ href: url })
        .setTextSelection(to) // move cursor to the very end of the selection
        .unsetLink() // turn off the link formatting for the next keystroke
        .run()
    }
  }
}
</script>

<style scoped>
.editor-container {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 10px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  flex-wrap: wrap;
}

.toolbar-btn {
  padding: 6px;
  background: none;
  border: none;
  border-radius: 4px;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  outline: none;
}

.toolbar-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.toolbar-btn.is-active {
  background: #454a83;
  color: #fff;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: #e2e8f0;
  margin: 0 4px;
}

.btn-clear:hover {
  color: #ef4444;
}

.editor-content {
  flex: 1;
  min-height: 150px;
  max-height: 400px;
  overflow-y: auto;
}

:deep(.tiptap) {
  padding: 14px;
  font-size: 14px;
  line-height: 1.6;
  color: #0f172a;
  outline: none;
  min-height: 150px;
  text-align: left;          
}

:deep(.tiptap p) {
  margin: 0 0 1em;
}

:deep(.tiptap h2) {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 1.5rem 0 0.75rem;
  color: #1e293b;
}

:deep(.tiptap h3) {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 1.25rem 0 0.5rem;
  color: #1e293b;
}

:deep(.tiptap ul), 
:deep(.tiptap ol) {
  padding-left: 1.5rem;
  margin: 0 0 1em;
}

:deep(.tiptap li) {
  margin-bottom: 0.25rem;
}

:deep(.tiptap a) {
  color: #454a83;
  text-decoration: underline;
  cursor: pointer;
}

:deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #94a3b8;
  pointer-events: none;
  height: 0;
}
</style>
