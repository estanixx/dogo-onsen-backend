import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

/**
 * Performance Tests para Dogo Onsen Backend
 * 
 * Requisitos No Funcionales cubiertos:
 * - RNF-001: Latencia en Lecturas p95 ≤ 300 ms
 * - RNF-002: Latencia en Escrituras ligeras p95 ≤ 400 ms
 * - RNF-003: Tiempo de respuesta API < 800 ms (contribución backend)
 * - RNF-005: Consistencia en recursos (prueba de carga concurrente)
 */

export const options = {
  scenarios: {
    // Escenario 1: Lecturas (RNF-001)
    read_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 }, // Ramp up to 10 users
        { duration: '1m', target: 10 },  // Stay at 10 users
        { duration: '30s', target: 0 },  // Ramp down
      ],
      exec: 'readEndpoints',
    },
    // Escenario 2: Escrituras ligeras (RNF-002)
    write_load: {
      executor: 'constant-vus',
      vus: 5,
      duration: '2m',
      exec: 'writeEndpoints',
    },
    // Escenario 3: Concurrencia en reservaciones (RNF-005)
    concurrent_reservations: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      exec: 'concurrentReservations',
      startTime: '2m30s', // Inicia después de los otros escenarios
    },
  },
  thresholds: {
    // RNF-001: Latencia en Lecturas p95 <= 300 ms
    'http_req_duration{type:read}': ['p(95)<300'],
    // RNF-002: Latencia en Escrituras ligeras p95 <= 400 ms
    'http_req_duration{type:write}': ['p(95)<400'],
    // RNF-003: Tiempo de respuesta general API
    'http_req_duration': ['p(95)<800'], 
    // General failure rate
    http_req_failed: ['rate<0.01'],
    // Métricas específicas por endpoint
    'http_req_duration{endpoint:employees}': ['p(95)<300'],
    'http_req_duration{endpoint:services}': ['p(95)<300'],
    'http_req_duration{endpoint:reservations}': ['p(95)<400'],
    'http_req_duration{endpoint:items}': ['p(95)<300'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8004';

// ==================== DEFAULT (para ejecución simple) ====================

export default function() {
  readEndpoints();
}

// ==================== LECTURAS (RNF-001) ====================

export function readEndpoints() {
  group('Read Operations', () => {
    // Leer empleados
    const empRes = http.get(`${BASE_URL}/employee`, {
      tags: { type: 'read', endpoint: 'employees' },
    });
    check(empRes, {
      'employees status 200': (r) => r.status === 200,
    });

    sleep(0.5);

    // Leer servicios
    const svcRes = http.get(`${BASE_URL}/service`, {
      tags: { type: 'read', endpoint: 'services' },
    });
    check(svcRes, {
      'services status 200': (r) => r.status === 200,
    });

    sleep(0.5);

    // Leer items de inventario
    const itemsRes = http.get(`${BASE_URL}/item`, {
      tags: { type: 'read', endpoint: 'items' },
    });
    check(itemsRes, {
      'items status 200': (r) => r.status === 200,
    });

    sleep(0.5);
  });
}

// ==================== ESCRITURAS (RNF-002) ====================

export function writeEndpoints() {
  group('Write Operations', () => {
    // Crear empleado
    const clerkId = `perf_${randomString(8)}`;
    const empPayload = JSON.stringify({
      clerkId: clerkId,
      firstName: 'Performance',
      lastName: 'Tester',
      email: `${clerkId}@example.com`,
      estado: 'pendiente'
    });

    const empRes = http.post(`${BASE_URL}/employee/`, empPayload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { type: 'write', endpoint: 'employees' },
    });

    check(empRes, {
      'create employee status 201': (r) => r.status === 201,
    });

    sleep(2);
  });
}

// ==================== CONCURRENCIA (RNF-005) ====================

export function concurrentReservations() {
  group('Concurrent Reservation Attempts', () => {
    // Simular múltiples usuarios intentando reservar
    // Este test verifica que el sistema maneja correctamente
    // solicitudes concurrentes sin errores 500

    const accountId = `acc_${randomString(6)}`;
    const reservationPayload = JSON.stringify({
      accountId: accountId,
      serviceId: 'svc_test',
      startTime: new Date(Date.now() + 3600000).toISOString(),
      endTime: new Date(Date.now() + 7200000).toISOString(),
    });

    const res = http.post(`${BASE_URL}/reservation/`, reservationPayload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { type: 'write', endpoint: 'reservations' },
    });

    // Aceptamos 201 (creado) o 409 (conflicto) o 422 (validación)
    // No debería haber errores 500
    check(res, {
      'reservation no server error': (r) => r.status !== 500,
      'reservation handled': (r) => [201, 409, 422, 400].includes(r.status),
    });

    sleep(0.5);
  });
}
