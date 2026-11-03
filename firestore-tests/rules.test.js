import { after, before, beforeEach, describe, it } from "node:test";
import { readFileSync } from "node:fs";
import {
  assertFails,
  assertSucceeds,
  initializeTestEnvironment,
} from "@firebase/rules-unit-testing";
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  getDoc,
  getDocs,
  query,
  setDoc,
  updateDoc,
  where,
} from "firebase/firestore";

let testEnv;

// Utilizatori: ana (proprietar), bob (urmărește pe ana), cris (străin), admin
const ana = () => testEnv.authenticatedContext("ana").firestore();
const bob = () => testEnv.authenticatedContext("bob").firestore();
const cris = () => testEnv.authenticatedContext("cris").firestore();
const admin = () => testEnv.authenticatedContext("adm", { admin: true }).firestore();
const anon = () => testEnv.unauthenticatedContext().firestore();

before(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: "demo-sporty-bara",
    firestore: { rules: readFileSync(new URL("../firestore.rules", import.meta.url), "utf8") },
  });
});

after(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  await testEnv.clearFirestore();
  await testEnv.withSecurityRulesDisabled(async (ctx) => {
    const db = ctx.firestore();
    await setDoc(doc(db, "users/ana"), { displayName: "Ana", balance: 1000 });
    await setDoc(doc(db, "users/bob"), { displayName: "Bob", balance: 1000 });
    await setDoc(doc(db, "profiles/ana"), { displayName: "Ana", rank: "pui" });
    await setDoc(doc(db, "matches/m1"), { home: "A", away: "B", status: "scheduled" });
    await setDoc(doc(db, "matches/m1/odds/superbet"), { home: 1.8, draw: 3.2, away: 4.1 });
    await setDoc(doc(db, "matches/m1/factors/f1"), { type: "injury", team: "home" });
    await setDoc(doc(db, "tickets/t1"), { uid: "ana", stake: 50, status: "open" });
    await setDoc(doc(db, "follows/bob/following/ana"), { createdAt: 1 });
    await setDoc(doc(db, "transactions/tx1"), { uid: "ana", amount: -50 });
    await setDoc(doc(db, "leagues/l1"), { name: "Balta", ownerUid: "ana", members: ["ana", "bob"] });
    await setDoc(doc(db, "leagues/l1/keys/ana"), { encryptedPrivateKey: "x" });
    await setDoc(doc(db, "league_stats/l1_ana"), { leagueId: "l1", uid: "ana", encProfit: "1" });
    await setDoc(doc(db, "wheel_config/current"), { prizes: [] });
    await setDoc(doc(db, "wheel_spins/s1"), { uid: "ana", prizeId: "p1" });
    await setDoc(doc(db, "cards/c1"), { uid: "ana", walletObjectId: "w" });
    await setDoc(doc(db, "nfc_tokens/tok"), { cardId: "c1", uid: "ana", used: false });
    await setDoc(doc(db, "pending_factors/pf1"), { matchId: "m1", status: "pending" });
    await setDoc(doc(db, "nepermis/x"), { a: 1 });
  });
});

describe("users", () => {
  it("proprietarul își citește documentul", async () => {
    await assertSucceeds(getDoc(doc(ana(), "users/ana")));
  });
  it("altcineva nu citește users", async () => {
    await assertFails(getDoc(doc(cris(), "users/ana")));
  });
  it("proprietarul NU își poate modifica balance", async () => {
    await assertFails(updateDoc(doc(ana(), "users/ana"), { balance: 999999 }));
  });
  it("proprietarul NU își poate suprascrie documentul", async () => {
    await assertFails(setDoc(doc(ana(), "users/ana"), { balance: 999999 }));
  });
  it("proprietarul NU își poate șterge documentul", async () => {
    await assertFails(deleteDoc(doc(ana(), "users/ana")));
  });
});

describe("profiles", () => {
  it("orice utilizator logat citește", async () => {
    await assertSucceeds(getDoc(doc(cris(), "profiles/ana")));
  });
  it("clientul nu scrie", async () => {
    await assertFails(updateDoc(doc(ana(), "profiles/ana"), { rank: "legenda" }));
  });
});

describe("matches", () => {
  it("logat citește meciul", async () => {
    await assertSucceeds(getDoc(doc(cris(), "matches/m1")));
  });
  it("logat citește odds", async () => {
    await assertSucceeds(getDoc(doc(cris(), "matches/m1/odds/superbet")));
  });
  it("logat citește factors", async () => {
    await assertSucceeds(getDoc(doc(cris(), "matches/m1/factors/f1")));
  });
  it("clientul nu scrie meciuri", async () => {
    await assertFails(updateDoc(doc(ana(), "matches/m1"), { status: "finished" }));
  });
  it("clientul nu scrie odds", async () => {
    await assertFails(setDoc(doc(ana(), "matches/m1/odds/x"), { home: 100 }));
  });
  it("clientul nu scrie factors", async () => {
    await assertFails(setDoc(doc(ana(), "matches/m1/factors/x"), { type: "news" }));
  });
});

describe("tickets", () => {
  it("proprietarul citește biletul", async () => {
    await assertSucceeds(getDoc(doc(ana(), "tickets/t1")));
  });
  it("cine îl urmărește pe proprietar citește biletul", async () => {
    await assertSucceeds(getDoc(doc(bob(), "tickets/t1")));
  });
  it("cine NU îl urmărește nu citește biletul", async () => {
    await assertFails(getDoc(doc(cris(), "tickets/t1")));
  });
  it("urmărirea e într-un singur sens (proprietarul nu vede biletele urmăritorului)", async () => {
    await testEnv.withSecurityRulesDisabled(async (ctx) => {
      await setDoc(doc(ctx.firestore(), "tickets/t2"), { uid: "bob", stake: 10 });
    });
    await assertFails(getDoc(doc(ana(), "tickets/t2")));
  });
  it("query filtrat pe uid propriu merge", async () => {
    await assertSucceeds(getDocs(query(collection(ana(), "tickets"), where("uid", "==", "ana"))));
  });
  it("query pe biletele altcuiva nenurmărit pică", async () => {
    await assertFails(getDocs(query(collection(cris(), "tickets"), where("uid", "==", "ana"))));
  });
  it("clientul NU poate crea bilete", async () => {
    await assertFails(addDoc(collection(ana(), "tickets"), { uid: "ana", stake: 10, status: "open" }));
  });
  it("proprietarul NU poate modifica biletul", async () => {
    await assertFails(updateDoc(doc(ana(), "tickets/t1"), { stake: 500 }));
  });
  it("proprietarul NU poate șterge biletul", async () => {
    await assertFails(deleteDoc(doc(ana(), "tickets/t1")));
  });
});

describe("transactions", () => {
  it("proprietarul citește tranzacția", async () => {
    await assertSucceeds(getDoc(doc(ana(), "transactions/tx1")));
  });
  it("altcineva NU citește tranzacția", async () => {
    await assertFails(getDoc(doc(bob(), "transactions/tx1")));
  });
  it("clientul nu creează tranzacții", async () => {
    await assertFails(addDoc(collection(ana(), "transactions"), { uid: "ana", amount: 1000 }));
  });
});

describe("leagues", () => {
  it("membrul citește liga", async () => {
    await assertSucceeds(getDoc(doc(bob(), "leagues/l1")));
  });
  it("non-membrul NU citește liga", async () => {
    await assertFails(getDoc(doc(cris(), "leagues/l1")));
  });
  it("query ligi după membru merge", async () => {
    await assertSucceeds(
      getDocs(query(collection(bob(), "leagues"), where("members", "array-contains", "bob")))
    );
  });
  it("clientul nu modifică liga (nici ca membru)", async () => {
    await assertFails(updateDoc(doc(ana(), "leagues/l1"), { members: ["ana", "cris"] }));
  });
  it("membrul își citește cheia", async () => {
    await assertSucceeds(getDoc(doc(ana(), "leagues/l1/keys/ana")));
  });
  it("membrul NU citește cheia altuia", async () => {
    await assertFails(getDoc(doc(bob(), "leagues/l1/keys/ana")));
  });
  it("non-membrul NU citește nici măcar cheia cu uid-ul lui", async () => {
    await testEnv.withSecurityRulesDisabled(async (ctx) => {
      await setDoc(doc(ctx.firestore(), "leagues/l1/keys/cris"), { encryptedPrivateKey: "y" });
    });
    await assertFails(getDoc(doc(cris(), "leagues/l1/keys/cris")));
  });
  it("clientul nu scrie chei", async () => {
    await assertFails(setDoc(doc(ana(), "leagues/l1/keys/ana"), { encryptedPrivateKey: "z" }));
  });
});

describe("league_stats", () => {
  it("membrul citește", async () => {
    await assertSucceeds(getDoc(doc(bob(), "league_stats/l1_ana")));
  });
  it("non-membrul NU citește", async () => {
    await assertFails(getDoc(doc(cris(), "league_stats/l1_ana")));
  });
  it("clientul nu scrie", async () => {
    await assertFails(setDoc(doc(ana(), "league_stats/l1_ana"), { leagueId: "l1", uid: "ana" }));
  });
});

describe("follows", () => {
  it("logat citește", async () => {
    await assertSucceeds(getDoc(doc(cris(), "follows/bob/following/ana")));
  });
  it("clientul nu scrie (follow trece prin funcție)", async () => {
    await assertFails(setDoc(doc(cris(), "follows/cris/following/ana"), { createdAt: 1 }));
  });
});

describe("wheel_config", () => {
  it("logat citește", async () => {
    await assertSucceeds(getDoc(doc(cris(), "wheel_config/current")));
  });
  it("clientul nu scrie", async () => {
    await assertFails(setDoc(doc(ana(), "wheel_config/current"), { prizes: [{ id: "x" }] }));
  });
});

describe("wheel_spins", () => {
  it("proprietarul citește", async () => {
    await assertSucceeds(getDoc(doc(ana(), "wheel_spins/s1")));
  });
  it("altcineva NU citește", async () => {
    await assertFails(getDoc(doc(bob(), "wheel_spins/s1")));
  });
  it("clientul nu scrie", async () => {
    await assertFails(addDoc(collection(ana(), "wheel_spins"), { uid: "ana", prizeId: "jackpot" }));
  });
});

describe("cards", () => {
  it("proprietarul citește", async () => {
    await assertSucceeds(getDoc(doc(ana(), "cards/c1")));
  });
  it("altcineva NU citește", async () => {
    await assertFails(getDoc(doc(bob(), "cards/c1")));
  });
  it("clientul nu scrie", async () => {
    await assertFails(setDoc(doc(ana(), "cards/c2"), { uid: "ana" }));
  });
});

describe("nfc_tokens", () => {
  it("nimeni nu citește (nici proprietarul)", async () => {
    await assertFails(getDoc(doc(ana(), "nfc_tokens/tok")));
  });
  it("nici adminul nu citește", async () => {
    await assertFails(getDoc(doc(admin(), "nfc_tokens/tok")));
  });
  it("nimeni nu scrie", async () => {
    await assertFails(setDoc(doc(ana(), "nfc_tokens/tok2"), { uid: "ana" }));
  });
});

describe("pending_factors", () => {
  it("adminul citește", async () => {
    await assertSucceeds(getDoc(doc(admin(), "pending_factors/pf1")));
  });
  it("non-adminul NU citește", async () => {
    await assertFails(getDoc(doc(ana(), "pending_factors/pf1")));
  });
  it("nici adminul nu scrie", async () => {
    await assertFails(updateDoc(doc(admin(), "pending_factors/pf1"), { status: "approved" }));
  });
});

describe("alte căi și neautentificat", () => {
  it("cale necunoscută: nimic", async () => {
    await assertFails(getDoc(doc(ana(), "nepermis/x")));
    await assertFails(setDoc(doc(ana(), "nepermis/y"), { a: 1 }));
  });
  it("neautentificatul nu citește nimic", async () => {
    const paths = [
      "users/ana",
      "profiles/ana",
      "matches/m1",
      "matches/m1/odds/superbet",
      "tickets/t1",
      "transactions/tx1",
      "leagues/l1",
      "leagues/l1/keys/ana",
      "league_stats/l1_ana",
      "follows/bob/following/ana",
      "wheel_config/current",
      "wheel_spins/s1",
      "cards/c1",
      "nfc_tokens/tok",
      "pending_factors/pf1",
    ];
    for (const p of paths) {
      await assertFails(getDoc(doc(anon(), p)));
    }
  });
  it("neautentificatul nu scrie", async () => {
    await assertFails(setDoc(doc(anon(), "users/ana"), { balance: 1 }));
  });
});
