import { trace, context, SpanStatusCode, Span } from '@opentelemetry/api'
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web'
import { registerInstrumentations } from '@opentelemetry/instrumentation'
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch'
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base'
import { Resource } from '@opentelemetry/resources'
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions'

let isInitialized = false
let tracer: ReturnType<typeof trace.getTracer> | null = null

/**
 * Initialize OpenTelemetry for frontend tracing.
 * Call this once at application startup.
 */
export function initTelemetry() {
  if (isInitialized || typeof window === 'undefined') {
    return
  }

  const provider = new WebTracerProvider({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: 'learnflow-frontend',
      [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    }),
  })

  // Configure OTLP exporter to send traces to backend
  const exporter = new OTLPTraceExporter({
    url: process.env.NEXT_PUBLIC_OTEL_EXPORTER_URL || 'http://localhost:4318/v1/traces',
  })

  provider.addSpanProcessor(new BatchSpanProcessor(exporter))
  provider.register()

  // Auto-instrument fetch calls
  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        propagateTraceHeaderCorsUrls: [
          new RegExp(process.env.NEXT_PUBLIC_KONG_URL || 'http://localhost:8000'),
        ],
        clearTimingResources: true,
        applyCustomAttributesOnSpan: (span: Span, request: Request | RequestInit, response: Response) => {
          span.setAttribute('http.request.url', request instanceof Request ? request.url : '')
          span.setAttribute('http.response.status_code', response.status)
        },
      }),
    ],
  })

  tracer = trace.getTracer('learnflow-frontend', '1.0.0')
  isInitialized = true
}

/**
 * Get the tracer instance.
 * Initializes telemetry if not already done.
 */
export function getTracer() {
  if (!tracer) {
    initTelemetry()
  }
  return tracer!
}

/**
 * Create a new span for tracing an operation.
 *
 * @param name - Name of the operation
 * @param fn - Function to execute within the span
 * @param attributes - Optional attributes to add to the span
 */
export async function withSpan<T>(
  name: string,
  fn: (span: Span) => Promise<T>,
  attributes?: Record<string, string | number | boolean>
): Promise<T> {
  const tracer = getTracer()

  return tracer.startActiveSpan(name, async (span) => {
    try {
      if (attributes) {
        Object.entries(attributes).forEach(([key, value]) => {
          span.setAttribute(key, value)
        })
      }

      const result = await fn(span)
      span.setStatus({ code: SpanStatusCode.OK })
      return result
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error instanceof Error ? error.message : 'Unknown error',
      })
      span.recordException(error as Error)
      throw error
    } finally {
      span.end()
    }
  })
}

/**
 * Trace a user interaction (button click, form submit, etc.)
 */
export function traceUserInteraction(
  action: string,
  attributes?: Record<string, string | number | boolean>
) {
  const tracer = getTracer()
  const span = tracer.startSpan(`user.${action}`, {
    attributes: {
      'user.action': action,
      ...attributes,
    },
  })
  span.end()
}

/**
 * Trace a page view.
 */
export function tracePageView(pagePath: string, attributes?: Record<string, string | number | boolean>) {
  const tracer = getTracer()
  const span = tracer.startSpan('page.view', {
    attributes: {
      'page.path': pagePath,
      'page.url': typeof window !== 'undefined' ? window.location.href : '',
      ...attributes,
    },
  })
  span.end()
}

/**
 * Trace an API call.
 */
export async function traceApiCall<T>(
  method: string,
  endpoint: string,
  fn: () => Promise<T>
): Promise<T> {
  return withSpan(
    `api.${method.toLowerCase()}.${endpoint}`,
    async (span) => {
      span.setAttribute('http.method', method)
      span.setAttribute('http.url', endpoint)
      return await fn()
    }
  )
}

/**
 * Trace a component render.
 */
export function traceComponentRender(componentName: string) {
  const tracer = getTracer()
  const span = tracer.startSpan(`component.render.${componentName}`)

  // Return a function to end the span
  return () => span.end()
}

/**
 * Add custom attributes to the current span.
 */
export function addSpanAttributes(attributes: Record<string, string | number | boolean>) {
  const currentSpan = trace.getActiveSpan()
  if (currentSpan) {
    Object.entries(attributes).forEach(([key, value]) => {
      currentSpan.setAttribute(key, value)
    })
  }
}

/**
 * Record an exception in the current span.
 */
export function recordException(error: Error) {
  const currentSpan = trace.getActiveSpan()
  if (currentSpan) {
    currentSpan.recordException(error)
    currentSpan.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    })
  }
}

/**
 * Get the current trace context for propagation.
 * Use this to pass trace context to backend API calls.
 */
export function getTraceContext(): Record<string, string> {
  const currentSpan = trace.getActiveSpan()
  if (!currentSpan) {
    return {}
  }

  const spanContext = currentSpan.spanContext()
  return {
    'traceparent': `00-${spanContext.traceId}-${spanContext.spanId}-01`,
  }
}
